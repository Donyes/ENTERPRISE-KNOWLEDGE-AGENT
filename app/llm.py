from langchain_openai import ChatOpenAI

from app.config import settings


def get_chat_model(temperature: float = 0.0) -> ChatOpenAI:
    """
    Create a ChatOpenAI model instance.

    temperature=0.0 makes the output more stable, which is better for
    enterprise RAG and evaluation.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
        temperature=temperature,
    )