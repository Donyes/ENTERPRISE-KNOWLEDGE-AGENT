from langchain_core.output_parsers import StrOutputParser

from app.llm import get_chat_model
from app.rag.prompts import basic_chat_prompt


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