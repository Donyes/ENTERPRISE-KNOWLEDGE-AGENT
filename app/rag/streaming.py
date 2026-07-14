import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.output_parsers import StrOutputParser

from app.llm import get_streaming_chat_model
from app.rag.advanced_retriever import retrieve_documents_with_score_filter
from app.rag.answerability import judge_answerability_async
from app.rag.formatter import format_documents_for_prompt, format_sources
from app.rag.prompts import rag_answer_prompt
from app.rag.query_rewrite import rewrite_query_async


def sse_event(event: str, data: dict[str, Any]) -> str:
    """
    Convert an event name and data dict into SSE format.

    SSE format:
    event: xxx
    data: {...}

    There must be a blank line after each event.
    """
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


async def retrieve_documents_with_score_filter_async(
    query: str,
    fetch_k: int = 8,
    final_k: int = 4,
    min_score: float | None = None,
) -> dict[str, Any]:
    """
    Run the current sync retriever in a worker thread.

    This prevents blocking the async event loop.
    """
    return await asyncio.to_thread(
        retrieve_documents_with_score_filter,
        query,
        fetch_k,
        final_k,
        min_score,
    )


def build_streaming_rag_answer_chain():
    """
    Build the streaming answer generation chain.

    Prompt -> Streaming Chat Model -> String Parser
    """
    model = get_streaming_chat_model(temperature=0.0)
    parser = StrOutputParser()

    chain = rag_answer_prompt | model | parser

    return chain


async def stream_advanced_rag_events(
    question: str,
    fetch_k: int = 8,
    final_k: int = 4,
    min_score: float | None = None,
    use_query_rewrite: bool = True,
) -> AsyncGenerator[str, None]:
    """
    Async streaming version of advanced RAG.

    This function yields SSE events:
    - status
    - rewritten_query
    - retrieval
    - answerability
    - token
    - sources
    - done
    """
    yield sse_event(
        "status",
        {
            "message": "开始处理用户问题。",
        },
    )

    if use_query_rewrite:
        yield sse_event(
            "status",
            {
                "message": "正在改写检索查询。",
            },
        )

        rewritten_query = await rewrite_query_async(question)
    else:
        rewritten_query = question

    yield sse_event(
        "rewritten_query",
        {
            "rewritten_query": rewritten_query,
        },
    )

    yield sse_event(
        "status",
        {
            "message": "正在检索知识库。",
        },
    )

    retrieval_result = await retrieve_documents_with_score_filter_async(
        query=rewritten_query,
        fetch_k=fetch_k,
        final_k=final_k,
        min_score=min_score,
    )

    documents = retrieval_result["documents"]
    sources = format_sources(documents)

    yield sse_event(
        "retrieval",
        {
            "retrieved_count": len(documents),
            "scores": retrieval_result["scores"],
            "debug_results": retrieval_result["debug_results"],
        },
    )

    context = format_documents_for_prompt(documents)

    yield sse_event(
        "status",
        {
            "message": "正在判断知识库资料是否足以回答。",
        },
    )

    answerability = await judge_answerability_async(
        question=question,
        context=context,
    )

    yield sse_event(
        "answerability",
        {
            "answerable": answerability["answerable"],
            "reason": answerability["reason"],
        },
    )

    if not documents or not answerability["answerable"]:
        refusal = "根据当前知识库资料，我无法确定。"

        yield sse_event(
            "token",
            {
                "text": refusal,
            },
        )

        yield sse_event(
            "sources",
            {
                "sources": sources,
            },
        )

        yield sse_event(
            "done",
            {
                "answer": refusal,
                "sources": sources,
                "answerable": False,
                "rewritten_query": rewritten_query,
            },
        )

        return

    yield sse_event(
        "status",
        {
            "message": "正在生成回答。",
        },
    )

    chain = build_streaming_rag_answer_chain()

    answer_parts: list[str] = []

    async for chunk in chain.astream(
        {
            "question": question,
            "context": context,
        }
    ):
        if not chunk:
            continue

        answer_parts.append(chunk)

        yield sse_event(
            "token",
            {
                "text": chunk,
            },
        )

    final_answer = "".join(answer_parts)

    yield sse_event(
        "sources",
        {
            "sources": sources,
        },
    )

    yield sse_event(
        "done",
        {
            "answer": final_answer,
            "sources": sources,
            "answerable": True,
            "rewritten_query": rewritten_query,
            "scores": retrieval_result["scores"],
        },
    )