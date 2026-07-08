from app.workflow.graph import run_ticket_workflow
from app.workflow.nodes import apply_review_decision


def run_case(message: str):
    print("=" * 100)
    print("User Input:")
    print(message)

    result = run_ticket_workflow(message)

    print("\nFinal Message:")
    print(result.get("final_message"))

    print("\nRequires Human Review:")
    print(result.get("requires_human_review"))

    print("\nAnswerable:")
    print(result.get("answerable"))

    print("\nTicket:")
    print(result.get("ticket"))

    return result


def main():
    case_1 = "差旅费报销需要哪些材料？"
    run_case(case_1)

    case_2 = "公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。"
    result = run_case(case_2)

    ticket_id = result.get("ticket_id")

    if ticket_id:
        print("\n" + "=" * 100)
        print("Human Review: approve ticket")
        review_result = apply_review_decision(
            ticket_id=ticket_id,
            approved=True,
            reviewer_comment="确认提交给相关部门处理。",
        )
        print(review_result)


if __name__ == "__main__":
    main()