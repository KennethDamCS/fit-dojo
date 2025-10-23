from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

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

@router.post("/login", response_model=Token)
def login(payload: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email is not verified")

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    # Optional: upgrade hash if parameters changed
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(payload.password)
        db.add(user); db.commit()

    access = create_token(user.email, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh = create_token(user.email, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

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

from pydantic import BaseModel
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

