import json
from pathlib import Path

import streamlit as st

from frontend.api_client import (
    agent_chat,
    chat_advanced_rag,
    create_ticket,
    list_tickets,
    review_workflow_ticket,
    run_workflow,
    stream_advanced_rag,
)


st.set_page_config(
    page_title="Enterprise Knowledge Agent",
    page_icon="🤖",
    layout="wide",
)


def show_json(data):
    st.json(data)


def page_home():
    st.title("Enterprise Knowledge Agent")
    st.write(
        """
        这是一个企业知识库 RAG + 工单处理 Agent 系统 Demo。

        当前系统包含：

        - 增强版 RAG 问答
        - Agent 工具调用
        - LangGraph 工作流
        - 工单管理
        - 评估结果展示
        """
    )

    st.subheader("推荐测试问题")

    st.code("差旅费报销需要哪些材料？")
    st.code("报销出差的钱要交什么东西？")
    st.code("试用期员工可以申请带薪年假吗？")
    st.code("VPN 首次使用需要做什么？")
    st.code("公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。")


def page_advanced_rag():
    st.title("增强版 RAG 问答")

    question = st.text_area(
        "请输入你的问题",
        value="差旅费报销需要哪些材料？",
        height=100,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        fetch_k = st.slider("fetch_k", min_value=1, max_value=20, value=8)

    with col2:
        final_k = st.slider("final_k", min_value=1, max_value=10, value=4)

    with col3:
        use_query_rewrite = st.checkbox("启用 Query Rewrite", value=True)

    mode = st.radio(
        "响应模式",
        options=["流式输出", "普通 JSON"],
        horizontal=True,
    )

    if st.button("运行增强版 RAG"):
        if mode == "普通 JSON":
            with st.spinner("正在检索知识库并生成答案..."):
                result = chat_advanced_rag(
                    question=question,
                    fetch_k=fetch_k,
                    final_k=final_k,
                    use_query_rewrite=use_query_rewrite,
                )

            st.subheader("回答")
            st.write(result.get("answer"))

            st.subheader("是否可回答")
            st.write(result.get("answerable"))

            st.subheader("改写后的查询")
            st.code(result.get("rewritten_query", ""))

            st.subheader("判断原因")
            st.write(result.get("answerability_reason"))

            st.subheader("引用来源")
            st.dataframe(result.get("sources", []))

            with st.expander("查看完整 JSON"):
                show_json(result)

        else:
            st.subheader("运行状态")
            status_box = st.empty()

            st.subheader("回答")
            answer_box = st.empty()

            st.subheader("元信息")
            meta_box = st.empty()

            final_answer = ""
            final_result = {}

            for item in stream_advanced_rag(
                question=question,
                fetch_k=fetch_k,
                final_k=final_k,
                use_query_rewrite=use_query_rewrite,
            ):
                event = item["event"]
                data = item["data"]

                if event == "status":
                    status_box.info(data.get("message", ""))

                elif event == "rewritten_query":
                    meta_box.write("改写后的查询：")
                    meta_box.code(data.get("rewritten_query", ""))

                elif event == "retrieval":
                    with st.expander("检索结果 Debug", expanded=False):
                        st.write(f"检索数量：{data.get('retrieved_count')}")
                        st.write("分数：")
                        st.write(data.get("scores"))
                        st.write("debug_results：")
                        st.json(data.get("debug_results"))

                elif event == "answerability":
                    st.write("Answerability：", data)

                elif event == "token":
                    final_answer += data.get("text", "")
                    answer_box.markdown(final_answer)

                elif event == "sources":
                    st.subheader("引用来源")
                    st.dataframe(data.get("sources", []))

                elif event == "done":
                    final_result = data
                    status_box.success("生成完成")

            with st.expander("查看最终结果 JSON"):
                st.json(final_result)


def page_agent():
    st.title("Agent 工具调用")

    message = st.text_area(
        "请输入你要交给 Agent 的任务",
        value="公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。",
        height=120,
    )

    include_debug = st.checkbox("显示 Debug Messages", value=True)

    if st.button("运行 Agent"):
        with st.spinner("Agent 正在判断意图并调用工具..."):
            result = agent_chat(
                message=message,
                include_debug=include_debug,
            )

        st.subheader("Agent 回复")
        st.write(result.get("answer"))

        if include_debug:
            with st.expander("查看 Agent 内部消息"):
                show_json(result.get("messages"))


def page_workflow():
    st.title("LangGraph 工作流")

    message = st.text_area(
        "请输入工作流任务",
        value="公司有没有免费午餐？如果知识库不知道，帮我生成一个工单草稿。",
        height=120,
    )

    if st.button("运行 Workflow"):
        with st.spinner("LangGraph 工作流运行中..."):
            result = run_workflow(message)

        st.session_state["last_workflow_result"] = result

        st.subheader("最终消息")
        st.write(result.get("final_message"))

        st.subheader("是否需要人工审核")
        st.write(result.get("requires_human_review"))

        st.subheader("工单信息")
        show_json(result.get("ticket"))

        with st.expander("查看完整 Workflow State"):
            show_json(result)

    st.divider()

    st.subheader("人工审核")

    last_result = st.session_state.get("last_workflow_result")
    default_ticket_id = 0

    if last_result and last_result.get("ticket_id"):
        default_ticket_id = int(last_result["ticket_id"])

    ticket_id = st.number_input(
        "工单 ID",
        min_value=0,
        value=default_ticket_id,
        step=1,
    )

    approved = st.radio(
        "审核结果",
        options=[True, False],
        format_func=lambda value: "通过并提交" if value else "拒绝",
    )

    reviewer_comment = st.text_input(
        "审核备注",
        value="确认提交给相关部门处理。",
    )

    if st.button("提交审核结果"):
        with st.spinner("正在更新工单状态..."):
            result = review_workflow_ticket(
                ticket_id=int(ticket_id),
                approved=approved,
                reviewer_comment=reviewer_comment,
            )

        st.subheader("审核结果")
        st.write(result.get("final_message"))
        show_json(result.get("ticket"))


def page_tickets():
    st.title("工单管理")

    st.subheader("创建手动工单")

    with st.form("create_ticket_form"):
        user_question = st.text_area(
            "用户问题",
            value="我的差旅费报销被拒了，帮我提交一个工单。",
        )
        category = st.selectbox(
            "分类",
            options=["finance", "it", "hr", "general"],
        )
        priority = st.selectbox(
            "优先级",
            options=["low", "medium", "high", "urgent"],
            index=1,
        )
        summary = st.text_area(
            "摘要",
            value="用户差旅费报销被拒，需要相关部门协助确认原因。",
        )

        submitted = st.form_submit_button("创建工单")

    if submitted:
        result = create_ticket(
            user_question=user_question,
            category=category,
            priority=priority,
            summary=summary,
        )

        st.success("工单创建成功")
        show_json(result)

    st.divider()

    st.subheader("工单列表")

    status_filter = st.selectbox(
        "状态筛选",
        options=["", "draft", "pending_review", "submitted", "resolved", "rejected"],
    )

    if st.button("刷新工单列表"):
        result = list_tickets(
            status=status_filter or None,
            limit=50,
        )

        st.write(f"共 {result.get('total')} 条工单")
        st.dataframe(result.get("tickets", []))

        with st.expander("查看完整 JSON"):
            show_json(result)


def page_evaluation():
    st.title("评估结果展示")

    rag_report_path = Path("data/evaluation/rag_evaluation_report.json")
    workflow_report_path = Path("data/evaluation/workflow_evaluation_report.json")

    if not rag_report_path.exists():
        st.warning("尚未找到 rag_evaluation_report.json，请先运行 python -m scripts.run_rag_eval。")
    else:
        rag_report = json.loads(rag_report_path.read_text(encoding="utf-8"))

        st.subheader("Basic RAG Summary")
        st.json(rag_report.get("basic_rag_summary", {}))

        st.subheader("Advanced RAG Summary")
        st.json(rag_report.get("advanced_rag_summary", {}))

    if not workflow_report_path.exists():
        st.warning("尚未找到 workflow_evaluation_report.json，请先运行 python -m scripts.run_workflow_eval。")
    else:
        workflow_report = json.loads(workflow_report_path.read_text(encoding="utf-8"))

        st.subheader("Workflow Summary")
        st.json(workflow_report.get("workflow_summary", {}))


def main():
    st.sidebar.title("导航")

    page = st.sidebar.radio(
        "选择页面",
        options=[
            "首页",
            "增强版 RAG",
            "Agent 工具调用",
            "LangGraph Workflow",
            "工单管理",
            "评估结果",
        ],
    )

    if page == "首页":
        page_home()
    elif page == "增强版 RAG":
        page_advanced_rag()
    elif page == "Agent 工具调用":
        page_agent()
    elif page == "LangGraph Workflow":
        page_workflow()
    elif page == "工单管理":
        page_tickets()
    elif page == "评估结果":
        page_evaluation()


if __name__ == "__main__":
    main()