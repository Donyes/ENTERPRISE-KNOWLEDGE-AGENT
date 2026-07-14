import json
import uuid
from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config import settings
from app.rag.embeddings import get_embedding_model


def load_chunks_from_jsonl(
    file_path: str = "data/processed/chunks.jsonl",
) -> List[Document]:
    """
    Load processed chunks from a JSONL file and convert them back to LangChain Documents.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Chunk file not found: {file_path}. "
            "Please run: python -m scripts.run_ingestion first."
        )

    documents = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            item = json.loads(line)

            documents.append(
                Document(
                    page_content=item["page_content"],
                    metadata=item.get("metadata", {}),
                )
            )

    return documents


def make_document_id(document: Document, fallback_index: int) -> str:
    """
    Create a stable UUID for each document chunk.

    Qdrant point IDs must be unsigned integers or UUID strings.
    We create a deterministic UUID from source + chunk_id so the same chunk
    gets the same ID every time the vector store is rebuilt.
    """
    metadata = document.metadata

    source = metadata.get("source", "unknown_source")
    chunk_id = metadata.get("chunk_id", fallback_index)

    raw_id = f"{source}::chunk_{chunk_id}"

    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw_id))


def get_qdrant_client() -> QdrantClient:
    """
    Create a Qdrant client.
    """
    if settings.qdrant_api_key:
        return QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

    return QdrantClient(
        url=settings.qdrant_url,
    )


def reset_vectorstore_collection() -> None:
    """
    Delete the existing Qdrant collection.

    This avoids duplicated chunks when rebuilding the vector store during development.
    """
    client = get_qdrant_client()

    if client.collection_exists(settings.qdrant_collection_name):
        client.delete_collection(settings.qdrant_collection_name)


def build_vectorstore_from_chunks(
    chunk_file_path: str = "data/processed/chunks.jsonl",
    reset: bool = True,
) -> QdrantVectorStore:
    """
    Build a Qdrant vector store from processed document chunks.
    """
    if reset:
        reset_vectorstore_collection()

    documents = load_chunks_from_jsonl(chunk_file_path)

    if not documents:
        raise ValueError("No documents found in chunk file.")

    embedding_model = get_embedding_model()

    ids = [
        make_document_id(document, index)
        for index, document in enumerate(documents)
    ]

    vectorstore = QdrantVectorStore.from_documents(
        documents,
        embedding_model,
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
        collection_name=settings.qdrant_collection_name,
        ids=ids,
    )

    return vectorstore


def load_vectorstore() -> QdrantVectorStore:
    """
    Load an existing Qdrant vector store collection.
    """
    embedding_model = get_embedding_model()

    vectorstore = QdrantVectorStore.from_existing_collection(
        embedding=embedding_model,
        collection_name=settings.qdrant_collection_name,
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )

    return vectorstore


def search_similar_documents(
    query: str,
    k: int = 4,
) -> List[Document]:
    """
    Search similar documents from Qdrant.
    """
    vectorstore = load_vectorstore()

    results = vectorstore.similarity_search(
        query=query,
        k=k,
    )

    return results


def search_similar_documents_with_scores(
    query: str,
    k: int = 8,
) -> List[Tuple[Document, float]]:
    """
    Search similar documents and return documents with similarity scores.

    For Qdrant, scores are similarity scores in LangChain's Qdrant integration.
    Higher score usually means more similar.
    """
    vectorstore = load_vectorstore()

    results = vectorstore.similarity_search_with_score(
        query=query,
        k=k,
    )

    return results