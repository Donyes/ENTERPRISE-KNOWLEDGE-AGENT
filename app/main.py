from fastapi import FastAPI
from app.config import settings
from app.schemas import (
    BasicChatRequest,
    BasicChatResponse,
    RAGChatRequest,
    RAGChatResponse,
    AdvancedRAGChatRequest,
    AdvancedRAGChatResponse,
)

from app.rag.chains import ask_basic_chat, ask_rag, ask_advanced_rag

from app.tickets.database import create_tables
from app.tickets.router import router as tickets_router
from app.agent.router import router as agent_router


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


create_tables()
app.include_router(tickets_router)
app.include_router(agent_router)

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


@app.post("/chat/rag/advanced", response_model=AdvancedRAGChatResponse)
def advanced_rag_chat(request: AdvancedRAGChatRequest):
    result = ask_advanced_rag(
        question=request.question,
        fetch_k=request.fetch_k,
        final_k=request.final_k,
        max_distance=request.max_distance,
        use_query_rewrite=request.use_query_rewrite,
    )

    return AdvancedRAGChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        retrieved_count=result["retrieved_count"],
        rewritten_query=result["rewritten_query"],
        answerable=result["answerable"],
        answerability_reason=result["answerability_reason"],
        scores=result["scores"],
        debug_results=result["debug_results"],
    )