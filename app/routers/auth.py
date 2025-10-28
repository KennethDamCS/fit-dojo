from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from sqlalchemy.orm import Session

from app.core.cookies import set_cookie, issue_csrf, require_csrf_if_cookie_auth, clear_cookie
from app.core.database import get_db
from app.core.emailer import send_email
from app.core.security import hash_password, verify_password, needs_rehash
from app.core.jwt_utils import create_token, create_typed_token, decode_token
from app.core.settings import settings
from app.core.deps import get_current_user
from app.models import EmailVerificationToken, PasswordResetToken
from app.schemas.auth import Login, Token
from app.schemas.user import UserCreate, UserOut
from app.models.user import User

from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        age=payload.age,
        sex=payload.sex,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        activity_level=payload.activity_level,
        goal=payload.goal,
    )
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.post("/login")
def login(payload: Login, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(payload.password)
        db.add(user); db.commit()

    access_token, _, _ = create_typed_token(user.email, settings.ACCESS_TOKEN_EXPIRE_MINUTES, "access")
    refresh_token, r_jti, r_exp = create_typed_token(user.email, settings.REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")

    set_cookie(response, settings.ACCESS_TOKEN_COOKIE, access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    set_cookie(response, settings.REFRESH_TOKEN_COOKIE, refresh_token, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    csrf = issue_csrf(response)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # keep for Swagger/manual testing; consider omitting in prod
        "token_type": "bearer",
        "csrf": csrf
    }

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/request-verify", status_code=200)
def request_verify(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"status": "ok"}  # don't leak accounts
    if user.is_verified:
        return {"status": "already_verified"}

    token, jti, exp = create_typed_token(user.email, settings.VERIFY_TOKEN_EXPIRE_MINUTES, "verify")
    db.add(EmailVerificationToken(user_id=user.id, jti=jti, expires_at=exp))
    db.commit()

    link = f"{settings.APP_BASE_URL}/auth/verify?token={token}"
    html = f"<p>Welcome to FitDojo!</p><p>Verify your email: <a href='{link}'>Verify</a></p>"
    send_email(user.email, "Verify your FitDojo email", html)
    return {"status": "sent"}

@router.get("/verify", status_code=200)
def verify(token: str = Query(...), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "verify":
        raise HTTPException(status_code=400, detail="Invalid token")
    email, jti = payload["sub"], payload.get("jti")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    rec = db.query(EmailVerificationToken).filter(EmailVerificationToken.jti == jti).first()
    if not rec or rec.used_at is not None or rec.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired or used")

    user.is_verified = True
    rec.used_at = datetime.now(timezone.utc)
    db.add_all([user, rec]); db.commit()
    return {"status": "verified"}

@router.post("/forgot-password", status_code=200)
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"status": "ok"}
    token, jti, exp = create_typed_token(user.email, settings.RESET_TOKEN_EXPIRE_MINUTES, "reset")
    db.add(PasswordResetToken(user_id=user.id, jti=jti, expires_at=exp))
    db.commit()

    link = f"{settings.APP_BASE_URL}/auth/reset-password?token={token}"
    html = f"<p>Reset your FitDojo password:</p><p><a href='{link}'>Set a new password</a></p>"
    send_email(user.email, "Reset your FitDojo password", html)
    return {"status": "sent"}

class ResetPasswordIn(BaseModel):
    token: str
    new_password: str

@router.post("/reset-password", status_code=200)
def reset_password(payload: ResetPasswordIn, db: Session = Depends(get_db)):
    data = decode_token(payload.token)
    if not data or data.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid token")
    email, jti = data["sub"], data.get("jti")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    rec = db.query(PasswordResetToken).filter(PasswordResetToken.jti == jti).first()
    if not rec or rec.used_at is not None or rec.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired or used")

    user.hashed_password = hash_password(payload.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    rec.used_at = datetime.now(timezone.utc)
    db.add_all([user, rec]); db.commit()
    return {"status": "password_updated"}

class RefreshIn(BaseModel):
    refresh_token: str | None = None  # allow body for Swagger, but prefer cookie

@router.post("/refresh")
def refresh(request: Request, response: Response, body: RefreshIn | None = None):
    # Enforce CSRF for cookie flow
    require_csrf_if_cookie_auth(request)

    # Prefer cookie token; fallback to body for Swagger/manual tests
    rt = request.cookies.get(settings.REFRESH_TOKEN_COOKIE)
    if not rt and body and body.refresh_token:
        rt = body.refresh_token
    if not rt:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    payload = decode_token(rt)
    if not payload or payload.get("type") != "refresh" or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token, _, _ = create_typed_token(payload["sub"], settings.ACCESS_TOKEN_EXPIRE_MINUTES, "access")
    new_refresh_token, _, _ = create_typed_token(payload["sub"], settings.REFRESH_TOKEN_EXPIRE_MINUTES, "refresh")

    set_cookie(response, settings.ACCESS_TOKEN_COOKIE, new_access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    set_cookie(response, settings.REFRESH_TOKEN_COOKIE, new_refresh_token, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    issue_csrf(response)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response, request: Request):
    require_csrf_if_cookie_auth(request)
    clear_cookie(response, settings.ACCESS_TOKEN_COOKIE)
    clear_cookie(response, settings.REFRESH_TOKEN_COOKIE)
    # also clear CSRF cookie
    clear_cookie(response, settings.CSRF_COOKIE)
    return {"status": "logged_out"}
