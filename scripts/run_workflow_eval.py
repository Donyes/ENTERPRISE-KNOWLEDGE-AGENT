import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.evaluation.dataset import load_eval_dataset
from app.evaluation.metrics import bool_to_score, ticket_creation_match
from app.observability.langsmith import setup_langsmith_tracing
from app.workflow.graph import run_ticket_workflow


def evaluate_workflow(example: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate the LangGraph workflow on one example.
    """
    question = example["question"]

    result = run_ticket_workflow(question)

    created_ticket = result.get("ticket_id") is not None

    ticket_ok = ticket_creation_match(
        created=created_ticket,
        should_create_ticket=example["should_create_ticket"],
    )

    answerable_ok = result.get("answerable") == example["expected_answerable"]

    return {
        "question": question,
        "final_message": result.get("final_message"),
        "answerable": result.get("answerable"),
        "requires_human_review": result.get("requires_human_review"),
        "ticket_id": result.get("ticket_id"),
        "ticket": result.get("ticket"),
        "ticket_creation_match": ticket_ok,
        "answerability_match": answerable_ok,
        "scores": {
            "ticket_creation_match": bool_to_score(ticket_ok),
            "answerability_match": bool_to_score(answerable_ok),
        },
    }


def summarize_results(results: list[dict[str, Any]]) -> dict[str, float]:
    """
    Summarize workflow evaluation results.
    """
    if not results:
        return {}

    metric_names = set()

    for item in results:
        metric_names.update(item["scores"].keys())

    summary = {}

    for metric_name in sorted(metric_names):
        values = [
            item["scores"][metric_name]
            for item in results
            if metric_name in item["scores"]
        ]

        summary[metric_name] = sum(values) / len(values)

    return summary


def main():
    setup_langsmith_tracing()

    dataset = load_eval_dataset()

    results = []

    for example in dataset:
        print("=" * 100)
        print(f"Evaluating workflow: {example['id']} - {example['question']}")

        result = evaluate_workflow(example)

        results.append(
            {
                "id": example["id"],
                "expected": example,
                "result": result,
            }
        )

        print(result["scores"])

    report = {
        "created_at": datetime.now().isoformat(),
        "dataset_size": len(dataset),
        "workflow_summary": summarize_results(
            [item["result"] for item in results]
        ),
        "workflow_results": results,
    }

    output_dir = Path("data/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "workflow_evaluation_report.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\nWorkflow evaluation finished.")
    print(f"Report saved to: {output_path}")

    print("\nWorkflow Summary:")
    print(report["workflow_summary"])


if __name__ == "__main__":
    main()