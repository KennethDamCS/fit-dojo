import os
from pydantic import BaseModel

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/fitdojo")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))
    JWT_ALGORITHM: str = "HS256"
    VERIFY_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("VERIFY_TOKEN_EXPIRE_MINUTES", "30"))
    RESET_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30"))
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    COOKIE_DOMAIN: str = os.getenv("COOKIE_DOMAIN", "localhost")
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "Lax")
    ACCESS_TOKEN_COOKIE: str = os.getenv("ACCESS_TOKEN_COOKIE", "fd_at")
    REFRESH_TOKEN_COOKIE: str = os.getenv("REFRESH_TOKEN_COOKIE", "fd_rt")
    CSRF_COOKIE: str = os.getenv("CSRF_COOKIE", "fd_csrf")

settings = Settings()