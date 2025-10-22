from fastapi import FastAPI
from app.routers import users
from app.routers import auth

app = FastAPI(title="FitDojo API")

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message":"Welcome to FitDojo"}

