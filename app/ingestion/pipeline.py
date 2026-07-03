import json
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from app.ingestion.loaders import load_documents_from_directory
from app.ingestion.splitter import split_documents


def document_to_dict(document: Document) -> dict:
    """
    Convert a LangChain Document to a serializable dict.
    """
    return {
        "page_content": document.page_content,
        "metadata": document.metadata,
    }


def save_documents_to_jsonl(documents: List[Document], output_path: str) -> None:
    """
    Save documents to a JSONL file.

    JSONL means one JSON object per line.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        for document in documents:
            f.write(json.dumps(document_to_dict(document), ensure_ascii=False) + "\n")


def run_ingestion_pipeline(
    input_dir: str = "data/raw",
    output_path: str = "data/processed/chunks.jsonl",
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> List[Document]:
    """
    Run the full ingestion pipeline:

    raw files -> documents -> chunks -> jsonl
    """
    raw_documents = load_documents_from_directory(input_dir)

    chunks = split_documents(
        raw_documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    save_documents_to_jsonl(chunks, output_path)

    return chunks