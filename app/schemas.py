from pydantic import BaseModel, Field


class BasicChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User question",
        examples=["What is a RAG system?"],
    )


class BasicChatResponse(BaseModel):
    answer: str