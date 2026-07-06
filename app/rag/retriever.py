from typing import List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.rag.vectorstore import load_vectorstore


def get_retriever(k: int = 4) -> BaseRetriever:
    """
    Create a retriever from the Chroma vector store.
    """
    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": k,
        },
    )

    return retriever


def retrieve_documents(query: str, k: int = 4) -> List[Document]:
    """
    Retrieve relevant documents using the vector store retriever.
    """
    retriever = get_retriever(k=k)

    documents = retriever.invoke(query)

    return documents