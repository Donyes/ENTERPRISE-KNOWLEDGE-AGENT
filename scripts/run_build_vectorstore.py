from app.rag.vectorstore import build_vectorstore_from_chunks, load_chunks_from_jsonl


def main():
    documents = load_chunks_from_jsonl("data/processed/chunks.jsonl")

    print(f"Loaded {len(documents)} chunks from data/processed/chunks.jsonl.")
    print("Building Chroma vector store...")

    build_vectorstore_from_chunks(
        chunk_file_path="data/processed/chunks.jsonl",
        reset=True,
    )

    print("Vector store built successfully.")
    print("Persist directory: data/vectorstore/chroma")


if __name__ == "__main__":
    main()