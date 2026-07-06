import json
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser

from app.llm import get_chat_model
from app.rag.prompts import answerability_prompt


def build_answerability_chain():
    """
    Build a chain to judge whether retrieved context can answer the question.
    """
    model = get_chat_model(temperature=0.0)
    parser = StrOutputParser()

    chain = answerability_prompt | model | parser

    return chain


def _safe_parse_json(text: str) -> Dict[str, Any]:
    """
    Safely parse model output as JSON.
    """
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Some models may wrap JSON with markdown code fences.
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "answerable": False,
            "reason": "模型未能输出合法 JSON，保守判断为不可回答。",
        }


def judge_answerability(question: str, context: str) -> Dict[str, Any]:
    """
    Judge whether the given context is sufficient to answer the question.
    """
    chain = build_answerability_chain()

    raw_result = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    parsed = _safe_parse_json(raw_result)

    answerable = bool(parsed.get("answerable", False))
    reason = str(parsed.get("reason", "")).strip()

    return {
        "answerable": answerable,
        "reason": reason,
        "raw_result": raw_result,
    }