import json
from pathlib import Path
from typing import Any


def load_eval_dataset(
    file_path: str = "data/evaluation/rag_eval_dataset.json",
) -> list[dict[str, Any]]:
    """
    Load evaluation dataset from JSON file.
    """
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data