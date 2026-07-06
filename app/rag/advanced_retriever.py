from typing import Any, Dict, List

from langchain_core.documents import Document

from app.rag.vectorstore import search_similar_documents_with_scores


def retrieve_documents_with_score_filter(
    query: str,
    fetch_k: int = 8,
    final_k: int = 4,
    max_distance: float | None = None,
) -> Dict[str, Any]:
    """
    Retrieve documents with scores and optionally filter by max distance.

    For Chroma distance scores, lower is usually more similar.
    """
    scored_results = search_similar_documents_with_scores(
        query=query,
        k=fetch_k,
    )

    debug_results = []

    for document, score in scored_results:
        debug_results.append(
            {
                "score": score,
                "file_name": document.metadata.get("file_name"),
                "source": document.metadata.get("source"),
                "page_number": document.metadata.get("page_number"),
                "chunk_id": document.metadata.get("chunk_id"),
                "preview": document.page_content[:120],
            }
        )

    if max_distance is not None:
        scored_results = [
            (document, score)
            for document, score in scored_results
            if score <= max_distance
        ]

    selected_results = scored_results[:final_k]

    documents: List[Document] = [
        document
        for document, _score in selected_results
    ]

    selected_scores = [
        score
        for _document, score in selected_results
    ]

    return {
        "documents": documents,
        "scores": selected_scores,
        "debug_results": debug_results,
    }