from pydantic import BaseModel, Field
from typing import Any, Dict, List

class BasicChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question",
        examples=["What is a RAG system?"],
    )


class BasicChatResponse(BaseModel):
    answer: str


class RAGChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question for knowledge-base RAG",
        examples=["差旅费报销需要哪些材料？"],
    )
    k: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of chunks to retrieve",
    )


class RAGChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_count: int


class AdvancedRAGChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question for advanced RAG",
        examples=["报销出差的钱要交什么东西？"],
    )
    fetch_k: int = Field(
        default=8,
        ge=1,
        le=30,
        description="Number of chunks to retrieve before filtering",
    )
    final_k: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of chunks to pass to the answer model",
    )
    min_score: float | None = Field(
        default=None,
        description="Optional minimum Qdrant similarity score for filtering results",
    )
    use_query_rewrite: bool = Field(
        default=True,
        description="Whether to rewrite the query before retrieval",
    )


class AdvancedRAGChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_count: int
    rewritten_query: str
    answerable: bool
    answerability_reason: str
    scores: List[float]
    debug_results: List[Dict[str, Any]]