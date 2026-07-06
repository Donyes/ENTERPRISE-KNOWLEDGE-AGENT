from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser

from app.llm import get_chat_model
from app.rag.formatter import format_documents_for_prompt, format_sources
from app.rag.prompts import basic_chat_prompt, rag_answer_prompt
from app.rag.retriever import retrieve_documents



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