from datetime import datetime, timedelta, timezone
import jwt  # PyJWT
from jwt.exceptions import InvalidTokenError
from app.core.settings import settings

def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())

def _exp(minutes: int) -> int:
    return int((datetime.now(timezone.utc) + timedelta(minutes=minutes)).timestamp())

def create_token(subject: str, expires_minutes: int) -> str:
    payload = {"sub": subject, "iat": _now_ts()}
    if expires_minutes:
        payload["exp"] = _exp(expires_minutes)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except InvalidTokenError:
        return None
