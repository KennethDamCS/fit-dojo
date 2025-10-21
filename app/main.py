from fastapi import FastAPI

app = FastAPI(title="FitDojo API")

@app.get("/")
def root():
    return {"message":"Welcome to FitDojo"}

