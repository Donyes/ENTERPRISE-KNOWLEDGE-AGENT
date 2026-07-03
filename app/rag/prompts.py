from langchain_core.prompts import ChatPromptTemplate


basic_chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an enterprise knowledge assistant. "
            "Answer clearly, accurately, and concisely. "
            "If you are not sure, say that you are not sure.",
        ),
        (
            "human",
            "{question}",
        ),
    ]
)