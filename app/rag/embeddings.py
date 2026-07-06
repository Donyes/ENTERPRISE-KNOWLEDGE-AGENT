from typing import Any

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import settings


def get_qwen_embedding_model() -> OpenAIEmbeddings:
    """
    Create a Qwen / Alibaba Bailian embedding model through
    the OpenAI-compatible embedding API.
    """
    if not settings.embedding_api_key:
        raise ValueError("EMBEDDING_API_KEY is missing. Please set it in your .env file.")

    if not settings.embedding_base_url:
        raise ValueError("EMBEDDING_BASE_URL is missing. Please set it in your .env file.")

    kwargs: dict[str, Any] = {
        "model": settings.embedding_model,
        "api_key": settings.embedding_api_key,
        "base_url": settings.embedding_base_url,

        # For Alibaba Bailian OpenAI-compatible embedding API:
        # it expects str or list[str], not token id arrays.
        "check_embedding_ctx_length": False,
        "tiktoken_enabled": False,
    }

    if settings.embedding_dimensions is not None:
        kwargs["dimensions"] = settings.embedding_dimensions

    return OpenAIEmbeddings(**kwargs)


def get_local_embedding_model() -> HuggingFaceEmbeddings:
    """
    Create a local HuggingFace embedding model as a fallback.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.local_embedding_model,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


def get_embedding_model():
    """
    Create the embedding model used for vector search.

    Supported providers:
    - qwen: use Alibaba Bailian / Qwen text-embedding-v4
    - local: use local HuggingFace embedding model
    """
    provider = settings.embedding_provider.lower()

    if provider == "qwen":
        return get_qwen_embedding_model()

    if provider == "local":
        return get_local_embedding_model()

    raise ValueError(
        f"Unsupported EMBEDDING_PROVIDER: {settings.embedding_provider}. "
        "Please use 'qwen' or 'local'."
    )