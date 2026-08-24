# Secure-rag

A small Retrieval-Augmented Generation (RAG) demo that indexes local documents and serves a FastAPI app for authenticated retrieval and question answering.

## Requirements
- Python 3.10+
- See `requirements.txt` for exact dependencies.

## Setup
1. Create and activate a virtual environment:

```powershell
python -m venv myenv
myenv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run
Start the FastAPI app with Uvicorn:

```powershell
uvicorn app:app --reload
```

Visit http://127.0.0.1:8000 for the API.

## Tests
Run unit tests with pytest:

```powershell
pytest -q
```

## Project structure
- `app.py` — FastAPI application entry
- `auth.py` — authentication helpers
- `rag.py` — retrieval and QA logic
- `vector_store.py` — vector persistence & Chroma integration
- `documents/` — sample text documents
- `db/` — Chroma database files

## Notes
- The project uses a local Chroma vector store (see `db/`).
- Update `requirements.txt` if you add packages.

---
Created by GitHub Copilot (assistant).