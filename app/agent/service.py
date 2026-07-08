from typing import Any

from langchain.agents import create_agent

from app.agent.prompts import ENTERPRISE_AGENT_SYSTEM_PROMPT
from app.agent.tools import ENTERPRISE_AGENT_TOOLS
from app.llm import get_chat_model


def build_enterprise_agent():
    """
    Build an enterprise agent with tools.
    """
    model = get_chat_model(temperature=0.0)

    agent = create_agent(
        model=model,
        tools=ENTERPRISE_AGENT_TOOLS,
        system_prompt=ENTERPRISE_AGENT_SYSTEM_PROMPT,
    )

    return agent


def _serialize_message(message) -> dict[str, Any]:
    """
    Convert a LangChain message into a JSON-serializable dict for debugging.
    """
    item = {
        "type": getattr(message, "type", message.__class__.__name__),
        "content": str(getattr(message, "content", "")),
    }

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        item["tool_calls"] = tool_calls

    name = getattr(message, "name", None)
    if name:
        item["name"] = name

    return item


def _extract_final_answer(result: dict[str, Any]) -> str:
    """
    Extract the final assistant answer from agent result.
    """
    messages = result.get("messages", [])

    if not messages:
        return str(result)

    final_message = messages[-1]
    content = getattr(final_message, "content", "")

    if isinstance(content, str):
        return content

    return str(content)


def run_enterprise_agent(
    user_input: str,
    include_debug: bool = False,
) -> dict[str, Any]:
    """
    Run the enterprise agent for one user input.
    """
    agent = build_enterprise_agent()

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        }
    )

    response = {
        "answer": _extract_final_answer(result),
    }

    if include_debug:
        response["messages"] = [
            _serialize_message(message)
            for message in result.get("messages", [])
        ]

    return response