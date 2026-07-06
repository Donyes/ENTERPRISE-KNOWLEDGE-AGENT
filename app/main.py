from fastapi import FastAPI
from app.config import settings
from app.schemas import (
    BasicChatRequest,
    BasicChatResponse,
    RAGChatRequest,
    RAGChatResponse,
)

from app.rag.chains import ask_basic_chat, ask_rag


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


@app.post("/chat/rag", response_model=RAGChatResponse)
def rag_chat(request: RAGChatRequest):
    result = ask_rag(
        question=request.question,
        k=request.k,
    )

    return RAGChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        retrieved_count=result["retrieved_count"],
    )