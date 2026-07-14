from app.rag.chains import ask_rag, ask_advanced_rag


def compare_one_question(question: str):
    print("=" * 100)
    print("Question:")
    print(question)

    print("\n" + "-" * 40)
    print("Basic RAG")
    print("-" * 40)
    basic_result = ask_rag(
        question=question,
        k=4,
    )
    print("Answer:")
    print(basic_result["answer"])
    print("Sources:")
    for source in basic_result["sources"]:
        print(source)

    print("\n" + "-" * 40)
    print("Advanced RAG")
    print("-" * 40)
    advanced_result = ask_advanced_rag(
        question=question,
        fetch_k=8,
        final_k=4,
        min_score=None,
        use_query_rewrite=True,
    )
    print("Rewritten Query:")
    print(advanced_result["rewritten_query"])
    print("Answerable:")
    print(advanced_result["answerable"])
    print("Answerability Reason:")
    print(advanced_result["answerability_reason"])
    print("Answer:")
    print(advanced_result["answer"])
    print("Scores:")
    print(advanced_result["scores"])
    print("Sources:")
    for source in advanced_result["sources"]:
        print(source)


def main():
    questions = [
        "差旅费报销需要哪些材料？",
        "报销出差的钱要交什么东西？",
        "我在家办公连不上公司系统，要先办什么？",
        "公司有没有免费午餐？",
    ]

    for question in questions:
        compare_one_question(question)


if __name__ == "__main__":
    main()