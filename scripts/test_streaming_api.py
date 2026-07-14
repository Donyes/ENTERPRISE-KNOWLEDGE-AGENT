import json

import requests


def parse_sse_line(line: str):
    if line.startswith("event: "):
        return "event", line.replace("event: ", "", 1)

    if line.startswith("data: "):
        data_text = line.replace("data: ", "", 1)
        return "data", json.loads(data_text)

    return None, None


def main():
    url = "http://127.0.0.1:8000/chat/rag/advanced/stream"

    payload = {
        "question": "差旅费报销需要哪些材料？",
        "fetch_k": 8,
        "final_k": 4,
        "min_score": None,
        "use_query_rewrite": True,
    }

    current_event = None

    with requests.post(url, json=payload, stream=True, timeout=120) as response:
        response.raise_for_status()

        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue

            kind, value = parse_sse_line(raw_line)

            if kind == "event":
                current_event = value

            elif kind == "data":
                if current_event == "token":
                    print(value.get("text", ""), end="", flush=True)
                else:
                    print(f"\n[{current_event}] {value}")


if __name__ == "__main__":
    main()