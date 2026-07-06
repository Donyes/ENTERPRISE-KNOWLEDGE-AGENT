# from app.rag.vectorstore import search_similar_documents
from app.rag.retriever import retrieve_documents

# def main():
#     query = "差旅费报销需要哪些材料？"
#     # query = "试用期员工可以申请带薪年假吗？"
#     # query = "VPN 首次使用需要做什么？"
#     # query = "员工忘记密码应该怎么办？"

#     results = search_similar_documents(
#         query=query,
#         k=3,
#     )

#     print(f"\nQuery: {query}")
#     print(f"Found {len(results)} similar chunks.\n")

#     for index, document in enumerate(results, start=1):
#         print("=" * 80)
#         print(f"Result {index}")
#         print("-" * 80)
#         print("Content:")
#         print(document.page_content[:500])

#         print("\nMetadata:")
#         print(document.metadata)


def main():
    query = "差旅费报销需要哪些材料？"

    results = retrieve_documents(
        query=query,
        k=3,
    )

    print(f"\nQuery: {query}")
    print(f"Found {len(results)} relevant chunks.\n")

    for index, document in enumerate(results, start=1):
        print("=" * 80)
        print(f"Result {index}")
        print("-" * 80)
        print("Content:")
        print(document.page_content[:500])

        print("\nMetadata:")
        print(document.metadata)

if __name__ == "__main__":
    main()