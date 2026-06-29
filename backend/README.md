# Backend

FastAPI backend for document upload, text extraction, chunking, embeddings, semantic search, and RAG chat.

## Current Structure

```text
backend/
├── app/
│   ├── main.py                FastAPI app and API routes
│   ├── database.py            SQLAlchemy setup and DB helper functions
│   ├── models.py              SQLAlchemy models
│   ├── schemas.py             Pydantic request schemas
│   ├── document_service.py    File validation, extraction, and chunking
│   ├── embedding_service.py   Ollama embedding generation
│   ├── llm_service.py         Ollama answer generation
│   ├── rag_service.py         RAG context and prompt building
│   └── file_store.py          Uploaded file persistence
└── README.md
```

## Recommended Structure

As the backend grows, split routes, services, repositories, and utilities into separate packages:

```text
backend/app/
├── main.py
├── config.py
├── database.py
├── models.py
├── schemas.py
├── api/
│   ├── health.py
│   ├── documents.py
│   ├── search.py
│   └── chat.py
├── services/
│   ├── document_service.py
│   ├── embedding_service.py
│   ├── retrieval_service.py
│   └── llm_service.py
├── repositories/
│   ├── document_repository.py
│   └── chunk_repository.py
└── utils/
    ├── file_store.py
    └── text_splitter.py
```

## Request Flow

Document upload:

```text
POST /documents/upload
  -> save uploaded file
  -> extract text
  -> split text into chunks
  -> generate embeddings with nomic-embed-text
  -> store document and chunks in Postgres/pgvector
```

Chat:

```text
POST /chat
  -> generate query embedding
  -> search similar chunks in pgvector
  -> build RAG context and prompt
  -> generate answer with llama3.2
  -> return answer with citations
```

## Run Application

Run from the `backend` directory:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

## Upload File

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@/Users/kamalsharma/Desktop/rag_teest1.txt" \
  -F "uploaded_by=kamal"
```

## List Documents

```bash
curl -X GET "http://localhost:8000/documents"
```

## Delete Document

```bash
curl -X DELETE "http://localhost:8000/documents/{document_id}"
```

## List Chunks

```bash
curl -X GET "http://localhost:8000/chunks"
```

## Search Documents

```bash
curl -s -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the document about?",
    "top_k": 3
  }' | jq
```

## Chat

```bash
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the story about?",
    "top_k": 3
  }' | jq
```

## DB Queries

Verify embeddings in the database:

```sql
SELECT
  chunk_index,
  LEFT(chunk_text, 80) AS preview,
  vector_dims(embedding) AS dimensions
FROM document_chunks;
```
