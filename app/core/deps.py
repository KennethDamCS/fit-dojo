from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as OrmSession

from app.core.database import get_db
from app.core.jwt_utils import decode_token
from app.core.settings import settings
from app.models.user import User
from app.models.session import Session as SessionModel

# Allow missing header so we can fall back to cookie
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: OrmSession = Depends(get_db),
) -> User:
    token: str | None = None

    # 1) Prefer Authorization header if present
    if creds and creds.scheme.lower() == "bearer":
        token = creds.credentials

    # 2) Else use access token cookie
    if not token:
        token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        )

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Enforce access tokens only (no refresh/verify/reset here)
    token_type = payload.get("type")
    if token_type is not None and token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong token type",
        )

    sub = payload["sub"]
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid subject in token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    jti = payload.get("jti")
    if not jti:
        # For our access tokens, we *expect* a JTI now
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session missing or invalid",
        )

    # Enforce that this JTI corresponds to a valid session
    session_row = (
        db.query(SessionModel)
        .filter(
            SessionModel.user_id == user.id,
            SessionModel.jti == jti,
        )
        .first()
    )
    if not session_row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalid or expired",
        )

    # Update last_seen_at
    session_row.last_seen_at = datetime.now(timezone.utc)
    db.add(session_row)
    db.commit()

    # Expose JTI for downstream routes (/auth/sessions, /auth/logout, /auth/logout-all)
    request.state.token_jti = jti

    return user
