from app.rag.chains import ask_advanced_rag


def run_case(question: str):
    result = ask_advanced_rag(
        question=question,
        fetch_k=8,
        final_k=4,
        # max_distance=None,
        max_distance=0.8,
        use_query_rewrite=True,
    )

    print("=" * 100)
    print("Question:")
    print(question)

    print("\nRewritten Query:")
    print(result["rewritten_query"])

    print("\nAnswerable:")
    print(result["answerable"])

    print("\nAnswerability Reason:")
    print(result["answerability_reason"])

    print("\nAnswer:")
    print(result["answer"])

    print("\nSelected Scores:")
    print(result["scores"])

    print("\nSources:")
    for index, source in enumerate(result["sources"], start=1):
        print("-" * 80)
        print(f"Source {index}:")
        print(source)

    print("\nDebug Retrieval Results:")
    for item in result["debug_results"]:
        print("-" * 80)
        print(item)


def main():
    questions = [
        "差旅费报销需要哪些材料？",
        "报销出差的钱要交什么东西？",
        "我在家办公连不上公司系统，要先办什么？",
        "试用期员工能休年假吗？",
        "公司有没有免费午餐？",
    ]

    for question in questions:
        run_case(question)


if __name__ == "__main__":
    main()