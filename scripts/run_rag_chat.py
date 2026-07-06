from app.rag.chains import ask_rag


def main():
    question = "差旅费报销需要哪些材料？一次能报销多少？"
    # question = "试用期员工可以申请带薪年假吗？"
    # question = "VPN 首次使用需要做什么？"
    # question = "员工忘记密码应该怎么办？"
    # question = "公司有没有提供免费午餐？"


    result = ask_rag(
        question=question,
        k=3,
    )

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(result["answer"])

    print("\nRetrieved Count:")
    print(result["retrieved_count"])

    print("\nSources:")
    for index, source in enumerate(result["sources"], start=1):
        print("=" * 80)
        print(f"Source {index}")
        print(source)


if __name__ == "__main__":
    main()