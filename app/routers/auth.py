from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, needs_rehash
from app.core.jwt_utils import create_token
from app.core.settings import settings
from app.core.deps import get_current_user
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
