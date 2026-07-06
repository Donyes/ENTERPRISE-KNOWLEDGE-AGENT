from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise Knowledge Agent"
    app_env: str = "development"

    # Chat model configuration
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Embedding model configuration
    embedding_provider: str = "qwen"
    embedding_api_key: str | None = None
    embedding_base_url: str | None = None
    embedding_model: str = "text-embedding-v4"
    embedding_dimensions: int | None = 1024

    # Local embedding fallback
    local_embedding_model: str = "BAAI/bge-small-zh-v1.5"

    # Chroma vector store
    chroma_persist_directory: str = "data/vectorstore/chroma"
    chroma_collection_name: str = "enterprise_knowledge_base"
    
    # LangSmith
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "enterprise-knowledge-agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()