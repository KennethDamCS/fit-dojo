# from fastapi import Depends, HTTPException, status, Request
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
#
#
# from app.core.database import get_db
# from app.core.jwt_utils import decode_token
# from app.core.settings import settings
# from app.models.user import User
#
# bearer_scheme = HTTPBearer(auto_error=True)
#
# def get_current_user(
#     request: Request,
#     creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
#     db: Session = Depends(get_db),
# ) -> User:
#     token = None
#     # 1) Prefer Authorization header if present
#     if creds and creds.scheme.lower() == "bearer":
#         token = creds.credentials
#     # 2) Else use cookie
#     if not token:
#         token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE)
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
#
#     payload = decode_token(token)
#     if not payload or "sub" not in payload:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#
#     user = db.query(User).filter(User.email == payload["sub"]).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#     return user


from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.jwt_utils import decode_token
from app.core.settings import settings
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)  # 👈 allow missing header

def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = None
    # 1) Prefer Authorization header if present
    if creds and creds.scheme.lower() == "bearer":
        token = creds.credentials
    # 2) Else use cookie
    if not token:
        token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
