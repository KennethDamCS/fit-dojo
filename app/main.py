from fastapi import FastAPI
from app.routers import users
from app.routers import auth

from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app.core.settings import settings

app = FastAPI(title="FitDojo API")

# CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_BASE_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Basic rate limiting (per IP)
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message":"Welcome to FitDojo"}

