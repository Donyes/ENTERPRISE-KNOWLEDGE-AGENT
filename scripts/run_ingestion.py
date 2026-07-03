from app.ingestion.pipeline import run_ingestion_pipeline


def main():
    chunks = run_ingestion_pipeline(
        input_dir="data/raw",
        output_path="data/processed/chunks.jsonl",
        chunk_size=800,
        chunk_overlap=120,
    )

    print(f"Generated {len(chunks)} chunks.\n")

    for chunk in chunks[:5]:
        print("=" * 80)
        print("Content Preview:")
        print(chunk.page_content[:300])
        print("\nMetadata:")
        print(chunk.metadata)


if __name__ == "__main__":
    main()