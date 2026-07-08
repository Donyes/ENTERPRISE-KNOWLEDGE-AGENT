# Enterprise Knowledge Agent

A job-oriented LLM application project that combines RAG, LangChain, LangGraph, LangSmith, FastAPI, Streamlit, and a ticket workflow.

## Features

- Enterprise document ingestion
- RAG-based question answering
- Citation-grounded answers
- Issue classification
- Ticket draft generation
- Human-in-the-loop approval
- LangGraph workflow orchestration
- LangSmith tracing and evaluation
- FastAPI backend
- Streamlit frontend
- Docker deployment

## Tech Stack

- Python
- FastAPI
- LangChain
- LangGraph
- LangSmith
- Chroma
- SQLAlchemy
- Streamlit
- Docker

## Project Structure

```text
enterprise-knowledge-agent/
├── app/
│   ├── ingestion/
│   ├── rag/
│   ├── agent/
│   ├── tickets/
│   └── evaluation/
├── frontend/
├── data/
├── tests/
└── README.md
```

# Quick Start

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Open:

[127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

# 0.11 初始化 Git

执行：

```powershell
git init
git add .
git commit -m "init project structure"
---
如果你还没配置 Git 用户名和邮箱，可能会报错。那就执行：

git config --global user.name "your-name"
git config --global user.email "your-email@example.com"

然后重新 commit。
```


## Evaluation

This project includes a small business-oriented evaluation dataset for RAG and workflow testing.

### Metrics

- Source hit: whether the retrieved sources include the expected document.
- Keyword recall: whether the generated answer contains expected key information.
- Answerability match: whether the system correctly decides if the question is answerable from the knowledge base.
- Ticket creation match: whether the workflow creates a ticket only when expected.

### Run evaluation

```bash
python -m scripts.run_rag_eval
python -m scripts.run_workflow_eval
python -m scripts.print_eval_summary
```

## Example results

| Module       | Metric                | Score        |
| ------------ | --------------------- | ------------ |
| Basic RAG    | Source hit            | to be filled |
| Basic RAG    | Keyword recall        | to be filled |
| Advanced RAG | Source hit            | to be filled |
| Advanced RAG | Answerability match   | to be filled |
| Workflow     | Ticket creation match | to be filled |
