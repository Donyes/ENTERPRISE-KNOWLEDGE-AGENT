from app.config import settings
from app.rag.vectorstore import build_vectorstore_from_chunks, load_chunks_from_jsonl


def main():
    documents = load_chunks_from_jsonl("data/processed/chunks.jsonl")

    print(f"Loaded {len(documents)} chunks from data/processed/chunks.jsonl.")
    print("Building Qdrant vector store...")

    build_vectorstore_from_chunks(
        chunk_file_path="data/processed/chunks.jsonl",
        reset=True,
    )

    print("Vector store built successfully.")
    print(f"Qdrant URL: {settings.qdrant_url}")
    print(f"Qdrant collection: {settings.qdrant_collection_name}")


if __name__ == "__main__":
    main()