from typing import Any


def normalize_text(text: str) -> str:
    """
    Normalize text for simple keyword matching.
    """
    return text.lower().replace(" ", "").replace("\n", "")


def keyword_recall(answer: str, expected_keywords: list[str]) -> dict[str, Any]:
    """
    Calculate how many expected keywords appear in the answer.
    """
    if not expected_keywords:
        return {
            "score": 1.0,
            "matched_keywords": [],
            "missing_keywords": [],
        }

    normalized_answer = normalize_text(answer)

    matched = []
    missing = []

    for keyword in expected_keywords:
        if normalize_text(keyword) in normalized_answer:
            matched.append(keyword)
        else:
            missing.append(keyword)

    score = len(matched) / len(expected_keywords)

    return {
        "score": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }


def source_hit(sources: list[dict[str, Any]], expected_source_file: str | None) -> bool:
    """
    Check whether the expected source file appears in retrieved sources.
    """
    if expected_source_file is None:
        return True

    for source in sources:
        file_name = source.get("file_name")
        if file_name == expected_source_file:
            return True

    return False


def answerability_match(
    predicted_answerable: bool,
    expected_answerable: bool,
) -> bool:
    """
    Check whether predicted answerability matches expected answerability.
    """
    return predicted_answerable == expected_answerable


def ticket_creation_match(
    created: bool,
    should_create_ticket: bool,
) -> bool:
    """
    Check whether ticket creation behavior matches expectation.
    """
    return created == should_create_ticket


def bool_to_score(value: bool) -> float:
    """
    Convert boolean metric to 0/1 score.
    """
    return 1.0 if value else 0.0