from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Enterprise Knowledge Agent API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.app_env,
    }