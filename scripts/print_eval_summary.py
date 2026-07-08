import json
from pathlib import Path


def load_json(path: str):
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def print_summary(title: str, summary: dict):
    print("=" * 80)
    print(title)
    print("=" * 80)

    for key, value in summary.items():
        print(f"{key}: {value:.2%}")


def main():
    rag_report_path = "data/evaluation/rag_evaluation_report.json"
    workflow_report_path = "data/evaluation/workflow_evaluation_report.json"

    rag_report = load_json(rag_report_path)
    workflow_report = load_json(workflow_report_path)

    print_summary(
        "Basic RAG Summary",
        rag_report["basic_rag_summary"],
    )

    print_summary(
        "Advanced RAG Summary",
        rag_report["advanced_rag_summary"],
    )

    print_summary(
        "Workflow Summary",
        workflow_report["workflow_summary"],
    )


if __name__ == "__main__":
    main()