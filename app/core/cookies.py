from fastapi import Response, Request, HTTPException, status
from secrets import token_urlsafe
from app.core.settings import settings

def set_cookie(resp: Response, name: str, value: str, minutes: int | None):
    max_age = minutes * 60 if minutes else None
    resp.set_cookie(
        key=name,
        value=value,
        max_age=max_age,
        httponly=True,                       # httpOnly for tokens
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )

def clear_cookie(resp: Response, name: str):
    resp.delete_cookie(
        key=name,
        domain=settings.COOKIE_DOMAIN,
        path="/"
    )

def issue_csrf(resp: Response) -> str:
    # double-submit cookie (readable by JS); not HttpOnly
    csrf = token_urlsafe(32)
    resp.set_cookie(
        key=settings.CSRF_COOKIE,
        value=csrf,
        max_age=60 * 60 * 12,                # 12h
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return csrf

def require_csrf_if_cookie_auth(request: Request):
    """
    For state-changing requests when using cookie auth:
    Enforce X-CSRF-Token == csrf cookie.
    Skip if Authorization: Bearer ... is used.
    """
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return  # header flow uses bearer; skip CSRF
    # cookie flow → enforce CSRF
    csrf_hdr = request.headers.get("x-csrf-token")
    csrf_cookie = request.cookies.get(settings.CSRF_COOKIE)
    if not csrf_hdr or not csrf_cookie or csrf_hdr != csrf_cookie:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")
