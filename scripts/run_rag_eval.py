import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.evaluation.dataset import load_eval_dataset
from app.evaluation.metrics import (
    answerability_match,
    bool_to_score,
    keyword_recall,
    source_hit,
)
from app.observability.langsmith import setup_langsmith_tracing
from app.rag.chains import ask_advanced_rag, ask_rag


def evaluate_basic_rag(example: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate the basic RAG pipeline on one example.
    """
    question = example["question"]

    result = ask_rag(
        question=question,
        k=4,
    )

    keyword_result = keyword_recall(
        answer=result["answer"],
        expected_keywords=example["expected_keywords"],
    )

    source_ok = source_hit(
        sources=result["sources"],
        expected_source_file=example["expected_source_file"],
    )

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
        "retrieved_count": result["retrieved_count"],
        "keyword_recall": keyword_result,
        "source_hit": source_ok,
        "scores": {
            "keyword_recall": keyword_result["score"],
            "source_hit": bool_to_score(source_ok),
        },
    }


def evaluate_advanced_rag(example: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate the advanced RAG pipeline on one example.
    """
    question = example["question"]

    result = ask_advanced_rag(
        question=question,
        fetch_k=8,
        final_k=4,
        max_distance=None,
        use_query_rewrite=True,
    )

    keyword_result = keyword_recall(
        answer=result["answer"],
        expected_keywords=example["expected_keywords"],
    )

    source_ok = source_hit(
        sources=result["sources"],
        expected_source_file=example["expected_source_file"],
    )

    answerability_ok = answerability_match(
        predicted_answerable=result["answerable"],
        expected_answerable=example["expected_answerable"],
    )

    return {
        "question": question,
        "rewritten_query": result["rewritten_query"],
        "answer": result["answer"],
        "answerable": result["answerable"],
        "answerability_reason": result["answerability_reason"],
        "sources": result["sources"],
        "retrieved_count": result["retrieved_count"],
        "scores_raw": result["scores"],
        "keyword_recall": keyword_result,
        "source_hit": source_ok,
        "answerability_match": answerability_ok,
        "scores": {
            "keyword_recall": keyword_result["score"],
            "source_hit": bool_to_score(source_ok),
            "answerability_match": bool_to_score(answerability_ok),
        },
    }


def summarize_results(results: list[dict[str, Any]]) -> dict[str, float]:
    """
    Summarize metric averages across examples.
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


def run_eval() -> dict[str, Any]:
    """
    Run evaluation for basic RAG and advanced RAG.
    """
    setup_langsmith_tracing()

    dataset = load_eval_dataset()

    basic_results = []
    advanced_results = []

    for example in dataset:
        print("=" * 100)
        print(f"Evaluating: {example['id']} - {example['question']}")

        basic_result = evaluate_basic_rag(example)
        advanced_result = evaluate_advanced_rag(example)

        basic_results.append(
            {
                "id": example["id"],
                "expected": example,
                "result": basic_result,
            }
        )

        advanced_results.append(
            {
                "id": example["id"],
                "expected": example,
                "result": advanced_result,
            }
        )

        print("Basic RAG scores:", basic_result["scores"])
        print("Advanced RAG scores:", advanced_result["scores"])

    report = {
        "created_at": datetime.now().isoformat(),
        "dataset_size": len(dataset),
        "basic_rag_summary": summarize_results(
            [item["result"] for item in basic_results]
        ),
        "advanced_rag_summary": summarize_results(
            [item["result"] for item in advanced_results]
        ),
        "basic_rag_results": basic_results,
        "advanced_rag_results": advanced_results,
    }

    return report


def main():
    report = run_eval()

    output_dir = Path("data/evaluation")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "rag_evaluation_report.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\nEvaluation finished.")
    print(f"Report saved to: {output_path}")

    print("\nBasic RAG Summary:")
    print(report["basic_rag_summary"])

    print("\nAdvanced RAG Summary:")
    print(report["advanced_rag_summary"])


if __name__ == "__main__":
    main()