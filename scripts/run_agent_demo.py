from app.agent.service import run_enterprise_agent


def run_case(user_input: str):
    print("=" * 100)
    print("User:")
    print(user_input)

    result = run_enterprise_agent(
        user_input=user_input,
        include_debug=True,
    )

    print("\nAgent Answer:")
    print(result["answer"])

    print("\nDebug Messages:")
    for message in result.get("messages", []):
        print("-" * 80)
        print(message)


def main():
    cases = [
        "差旅费报销需要哪些材料？",
        "报销出差的钱要交什么东西？",
        "公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。",
        "帮我查看当前有哪些工单。",
    ]

    for case in cases:
        run_case(case)


if __name__ == "__main__":
    main()