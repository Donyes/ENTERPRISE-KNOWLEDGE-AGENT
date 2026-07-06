import json
import shutil
from pathlib import Path
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import settings
from app.rag.embeddings import get_embedding_model


def load_chunks_from_jsonl(file_path: str = "data/processed/chunks.jsonl") -> List[Document]:
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
    Create a stable id for each document chunk.
    """
    metadata = document.metadata

    source = metadata.get("source", "unknown_source")
    chunk_id = metadata.get("chunk_id", fallback_index)

    return f"{source}::chunk_{chunk_id}"


def reset_vectorstore_directory() -> None:
    """
    Remove the existing Chroma persistence directory.

    This avoids duplicated chunks when rebuilding the vector store during development.
    """
    persist_path = Path(settings.chroma_persist_directory)

    if persist_path.exists():
        shutil.rmtree(persist_path)


def create_empty_vectorstore() -> Chroma:
    """
    Create a Chroma vector store instance.
    """
    embedding_model = get_embedding_model()

    vectorstore = Chroma(
        collection_name=settings.chroma_collection_name,
        embedding_function=embedding_model,
        persist_directory=settings.chroma_persist_directory,
    )

    return vectorstore


def build_vectorstore_from_chunks(
    chunk_file_path: str = "data/processed/chunks.jsonl",
    reset: bool = True,
) -> Chroma:
    """
    Build a Chroma vector store from processed document chunks.
    """
    if reset:
        reset_vectorstore_directory()

    documents = load_chunks_from_jsonl(chunk_file_path)

    if not documents:
        raise ValueError("No documents found in chunk file.")

    vectorstore = create_empty_vectorstore()

    ids = [
        make_document_id(document, index)
        for index, document in enumerate(documents)
    ]

    vectorstore.add_documents(
        documents=documents,
        ids=ids,
    )

    return vectorstore


def load_vectorstore() -> Chroma:
    """
    Load an existing Chroma vector store from disk.
    """
    persist_path = Path(settings.chroma_persist_directory)

    if not persist_path.exists():
        raise FileNotFoundError(
            f"Vector store not found at {settings.chroma_persist_directory}. "
            "Please run: python -m scripts.run_build_vectorstore first."
        )

    return create_empty_vectorstore()


def search_similar_documents(
    query: str,
    k: int = 4,
) -> List[Document]:
    """
    Search similar documents from the vector store.
    """
    vectorstore = load_vectorstore()

    results = vectorstore.similarity_search(
        query=query,
        k=k,
    )

    return results