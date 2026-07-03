from app.rag.chains import ask_basic_chat


def main():
    # question = "What is the purpose of a RAG system in enterprise knowledge management?"
    question = "企业知识管理中RAG系统的作用是什么？"
    answer = ask_basic_chat(question)

    print("\nQuestion:")
    print(question)

    print("\nAnswer:")
    print(answer)


if __name__ == "__main__":
    main()