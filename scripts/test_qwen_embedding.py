from app.rag.embeddings import get_embedding_model


def main():
    embedding_model = get_embedding_model()

    texts = [
        "差旅费报销需要提供出差审批单、交通票据、住宿发票、行程单以及费用明细表。",
        "员工远程办公时需要使用公司 VPN。",
    ]

    vectors = embedding_model.embed_documents(texts)

    print(f"Generated {len(vectors)} embeddings.")
    print(f"Embedding dimension: {len(vectors[0])}")
    print(f"First 5 values: {vectors[0][:5]}")


if __name__ == "__main__":
    main()