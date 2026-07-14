from app.observability.langsmith import setup_langsmith_tracing
from app.rag.chains import ask_advanced_rag
from app.workflow.graph import run_ticket_workflow


def main():
    setup_langsmith_tracing()

    print("Running advanced RAG trace demo...")

    rag_result = ask_advanced_rag(
        question="差旅费报销需要哪些材料？",
        fetch_k=8,
        final_k=4,
        min_score=None,
        use_query_rewrite=True,
    )

    print("\nRAG Answer:")
    print(rag_result["answer"])

    print("\nRunning workflow trace demo...")

    workflow_result = run_ticket_workflow(
        "公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。"
    )

    print("\nWorkflow Final Message:")
    print(workflow_result.get("final_message"))


if __name__ == "__main__":
    main()