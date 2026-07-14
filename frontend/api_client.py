import json
import os
from collections.abc import Generator
from typing import Any

import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{API_BASE_URL}{path}"

    response = requests.post(
        url,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def _get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{API_BASE_URL}{path}"

    response = requests.get(
        url,
        params=params,
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def chat_advanced_rag(
    question: str,
    fetch_k: int = 8,
    final_k: int = 4,
    use_query_rewrite: bool = True,
) -> dict[str, Any]:
    return _post(
        "/chat/rag/advanced",
        {
            "question": question,
            "fetch_k": fetch_k,
            "final_k": final_k,
            "min_score": None,
            "use_query_rewrite": use_query_rewrite,
        },
    )


def agent_chat(
    message: str,
    include_debug: bool = False,
) -> dict[str, Any]:
    return _post(
        "/agent/chat",
        {
            "message": message,
            "include_debug": include_debug,
        },
    )


def run_workflow(message: str) -> dict[str, Any]:
    return _post(
        "/workflow/run",
        {
            "message": message,
        },
    )


def review_workflow_ticket(
    ticket_id: int,
    approved: bool,
    reviewer_comment: str | None = None,
) -> dict[str, Any]:
    return _post(
        "/workflow/review",
        {
            "ticket_id": ticket_id,
            "approved": approved,
            "reviewer_comment": reviewer_comment,
        },
    )


def list_tickets(
    status: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "limit": limit,
    }

    if status:
        params["status"] = status

    return _get(
        "/tickets",
        params=params,
    )


def create_ticket(
    user_question: str,
    category: str,
    priority: str,
    summary: str,
) -> dict[str, Any]:
    return _post(
        "/tickets",
        {
            "user_question": user_question,
            "category": category,
            "priority": priority,
            "summary": summary,
            "evidence": [],
        },
    )

def stream_advanced_rag(
    question: str,
    fetch_k: int = 8,
    final_k: int = 4,
    min_score: float | None = None,
    use_query_rewrite: bool = True,
) -> Generator[dict[str, Any], None, None]:
    """
    Stream advanced RAG events from backend SSE endpoint.

    Yields dicts like:
    {
        "event": "token",
        "data": {"text": "..."}
    }
    """
    url = f"{API_BASE_URL}/chat/rag/advanced/stream"

    payload = {
        "question": question,
        "fetch_k": fetch_k,
        "final_k": final_k,
        "min_score": min_score,
        "use_query_rewrite": use_query_rewrite,
    }

    current_event = None

    with requests.post(
        url,
        json=payload,
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue

            if raw_line.startswith("event: "):
                current_event = raw_line.replace("event: ", "", 1)
                continue

            if raw_line.startswith("data: "):
                data_text = raw_line.replace("data: ", "", 1)
                data = json.loads(data_text)

                yield {
                    "event": current_event,
                    "data": data,
                }