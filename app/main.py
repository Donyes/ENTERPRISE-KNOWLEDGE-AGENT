from fastapi import FastAPI
from app.config import settings
from app.schemas import BasicChatRequest, BasicChatResponse
from app.rag.chains import ask_basic_chat


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

@app.post("/chat/basic", response_model=BasicChatResponse)
def basic_chat(request: BasicChatRequest):
    answer = ask_basic_chat(request.question)

    return BasicChatResponse(answer=answer)