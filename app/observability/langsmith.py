import os

from app.config import settings


def setup_langsmith_tracing() -> None:
    """
    Configure LangSmith tracing from project settings.

    LangChain and LangGraph read these environment variables automatically.
    """
    os.environ["LANGSMITH_TRACING"] = "true" if settings.langsmith_tracing else "false"

    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key

    if settings.langsmith_project:
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project