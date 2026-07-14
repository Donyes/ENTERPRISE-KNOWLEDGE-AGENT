from langchain_core.output_parsers import StrOutputParser

from app.llm import get_chat_model
from app.rag.prompts import query_rewrite_prompt


def build_query_rewrite_chain():
    """
    Build a query rewrite chain.

    User question -> rewritten retrieval query
    """
    model = get_chat_model(temperature=0.0)
    parser = StrOutputParser()

    chain = query_rewrite_prompt | model | parser

    return chain


def rewrite_query(question: str) -> str:
    """
    Rewrite the user's question into a better retrieval query.
    """
    chain = build_query_rewrite_chain()

    rewritten_query = chain.invoke(
        {
            "question": question,
        }
    )

    rewritten_query = rewritten_query.strip()

    if not rewritten_query:
        return question

    return rewritten_query

async def rewrite_query_async(question: str) -> str:
    """
    Async version of query rewrite.

    Used by async streaming RAG pipeline.
    """
    chain = build_query_rewrite_chain()

    rewritten_query = await chain.ainvoke(
        {
            "question": question,
        }
    )

    rewritten_query = rewritten_query.strip()

    if not rewritten_query:
        return question

    return rewritten_query