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