from typing import List

from langchain_core.documents import Document


def format_documents_for_prompt(documents: List[Document]) -> str:
    """
    Convert retrieved documents into a context string for the RAG prompt.
    """
    if not documents:
        return "未检索到相关知识库内容。"

    formatted_chunks = []

    for index, document in enumerate(documents, start=1):
        metadata = document.metadata

        file_name = metadata.get("file_name", "unknown_file")
        page_number = metadata.get("page_number")
        chunk_id = metadata.get("chunk_id", "unknown_chunk")

        source_line = f"来源 {index}: {file_name}"

        if page_number is not None:
            source_line += f"，第 {page_number} 页"

        source_line += f"，chunk_id={chunk_id}"

        formatted_chunk = f"""
{source_line}

内容：
{document.page_content}
""".strip()

        formatted_chunks.append(formatted_chunk)

    return "\n\n---\n\n".join(formatted_chunks)


def format_sources(documents: List[Document]) -> List[dict]:
    """
    Convert retrieved documents into source metadata for API response.
    """
    sources = []

    for document in documents:
        metadata = document.metadata

        sources.append(
            {
                "file_name": metadata.get("file_name"),
                "source": metadata.get("source"),
                "file_type": metadata.get("file_type"),
                "page_number": metadata.get("page_number"),
                "chunk_id": metadata.get("chunk_id"),
                "chunk_size": metadata.get("chunk_size"),
                "preview": document.page_content[:120],
            }
        )

    return sources