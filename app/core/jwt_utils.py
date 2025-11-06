from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from app.core.settings import settings


# Utility
def _now() -> datetime:
    return datetime.now(timezone.utc)


# 🔸 Generic token creator (used for access, refresh, etc.)
def create_token(
    subject: str,
    expires_minutes: int,
    *,
    jti: str | None = None,
    typ: str | None = None,
) -> str:
    """
    Create a JWT with required claims + optional type and jti.

    - subject: usually user ID
    - expires_minutes: expiry in minutes
    - jti: optional token/session ID
    - typ: optional logical type, e.g. "access", "refresh", "verify", "reset"
    """
    now = _now()
    payload: dict[str, object] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }

    if typ is not None:
        payload["type"] = typ
    if jti is not None:
        payload["jti"] = jti

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# 🔸 Typed/single-use tokens (email verify & password reset)
def create_typed_token(
    subject: str,
    minutes: int,
    typ: str,
) -> tuple[str, str, datetime]:
    """
    Create a one-time-use token (verify/reset) with its own JTI.

    Returns (token, jti, exp) so you can store jti+exp in the DB.
    """
    jti = uuid4().hex
    now = _now()
    exp = now + timedelta(minutes=minutes)

    payload: dict[str, object] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": typ,   # e.g. "verify" or "reset"
        "jti": jti,    # unique token ID for one-time use
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
