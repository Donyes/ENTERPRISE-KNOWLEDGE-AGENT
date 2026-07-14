from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser

from app.llm import get_chat_model
from app.rag.formatter import format_documents_for_prompt, format_sources
from app.rag.prompts import basic_chat_prompt, rag_answer_prompt
from app.rag.retriever import retrieve_documents

from app.rag.advanced_retriever import retrieve_documents_with_score_filter
from app.rag.answerability import judge_answerability
from app.rag.query_rewrite import rewrite_query


def build_basic_chat_chain():
    """
    Build a minimal LCEL chain:

    Prompt -> Chat Model -> String Parser
    """
    model = get_chat_model(temperature=0.0)
    parser = StrOutputParser()

    chain = basic_chat_prompt | model | parser

    return chain


def ask_basic_chat(question: str) -> str:
    """
    Ask a question using the minimal LCEL chain.
    """
    chain = build_basic_chat_chain()

    answer = chain.invoke(
        {
            "question": question,
        }
    )

    return answer

def build_rag_answer_chain():
    """
    Build the answer-generation part of the RAG pipeline:

    RAG Prompt -> Chat Model -> String Parser
    """
    model = get_chat_model(temperature=0.0)
    parser = StrOutputParser()

    chain = rag_answer_prompt | model | parser

    return chain


def ask_rag(question: str, k: int = 4) -> Dict[str, Any]:
    """
    Ask a question using the basic RAG pipeline.

    Steps:
    1. Retrieve relevant documents.
    2. Format documents as context.
    3. Generate an answer based on the context.
    4. Return answer and sources.
    """
    documents = retrieve_documents(
        query=question,
        k=k,
    )

    context = format_documents_for_prompt(documents)

    chain = build_rag_answer_chain()

    answer = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    return {
        "answer": answer,
        "sources": format_sources(documents),
        "retrieved_count": len(documents),
    }


def ask_advanced_rag(
    question: str,
    fetch_k: int = 8,
    final_k: int = 4,
    min_score: float | None = None,
    use_query_rewrite: bool = True,
) -> Dict[str, Any]:
    """
    Ask a question using an enhanced RAG pipeline.

    Steps:
    1. Rewrite the query if enabled.
    2. Retrieve documents with scores.
    3. Filter noisy retrieval results.
    4. Format context.
    5. Judge whether the context can answer the question.
    6. Generate answer or refuse to answer.
    """
    rewritten_query = rewrite_query(question) if use_query_rewrite else question

    retrieval_result = retrieve_documents_with_score_filter(
        query=rewritten_query,
        fetch_k=fetch_k,
        final_k=final_k,
        min_score=min_score,
    )

    documents = retrieval_result["documents"]
    context = format_documents_for_prompt(documents)

    answerability = judge_answerability(
        question=question,
        context=context,
    )

    if not documents or not answerability["answerable"]:
        return {
            "answer": "根据当前知识库资料，我无法确定。",
            "sources": format_sources(documents),
            "retrieved_count": len(documents),
            "rewritten_query": rewritten_query,
            "answerable": False,
            "answerability_reason": answerability["reason"],
            "scores": retrieval_result["scores"],
            "debug_results": retrieval_result["debug_results"],
        }

    chain = build_rag_answer_chain()

    answer = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    return {
        "answer": answer,
        "sources": format_sources(documents),
        "retrieved_count": len(documents),
        "rewritten_query": rewritten_query,
        "answerable": True,
        "answerability_reason": answerability["reason"],
        "scores": retrieval_result["scores"],
        "debug_results": retrieval_result["debug_results"],
    }