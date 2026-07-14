from app.config import settings
from app.rag.vectorstore import get_qdrant_client


def main():
    client = get_qdrant_client()

    collections = client.get_collections()

    print("Qdrant connection OK.")
    print(f"Qdrant URL: {settings.qdrant_url}")
    print("Collections:")
    print(collections)


if __name__ == "__main__":
    main()