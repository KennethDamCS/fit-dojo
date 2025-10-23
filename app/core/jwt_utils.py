from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from uuid import uuid4
from app.core.settings import settings

# Utility
def _now() -> datetime:
    return datetime.now(timezone.utc)

# 🔸 Create regular access/refresh tokens
def create_token(subject: str, expires_minutes: int) -> str:
    now = _now()
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# 🔸 Create typed/single-use tokens (for email verify & password reset)
def create_typed_token(subject: str, minutes: int, typ: str) -> tuple[str, str, datetime]:
    jti = uuid4().hex
    now = _now()
    exp = now + timedelta(minutes=minutes)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": typ,  # e.g. "verify" or "reset"
        "jti": jti,   # unique token ID for one-time use
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, exp

# 🔸 Decode token safely (handles expiry & invalid)
def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp"]},
            leeway=5,  # small tolerance for clock skew
        )
    except (ExpiredSignatureError, InvalidTokenError):
        return None
