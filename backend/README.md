# Backend

FastAPI backend for document upload, text extraction, chunking, embeddings, semantic search, and RAG chat.

## Current Structure

```text
backend/
├── app/
│   ├── api/                   FastAPI routes
│   ├── services/              Business workflows and AI integrations
│   │   ├── chunking_service.py
│   │   └── document_service.py
│   ├── repositories/          Database operations
│   ├── utils/                 Small helper functions
│   ├── main.py                FastAPI app setup
│   ├── config.py              App constants and environment values
│   ├── database.py            SQLAlchemy setup and DB helper functions
│   ├── models.py              SQLAlchemy models
│   └── schemas.py             Pydantic request schemas
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
│   └── chat.py
├── services/
│   ├── chunking_service.py
│   ├── document_service.py
│   ├── embedding_service.py
│   ├── retrieval_service.py
│   └── llm_service.py
├── repositories/
│   ├── document_repository.py
│   └── chunk_repository.py
└── utils/
    └── file_store.py
```

## Request Flow

Document upload:

```text
POST /documents/upload
  -> save uploaded file
  -> extract text
  -> split text into paragraph-aware chunks
  -> generate embeddings with nomic-embed-text
  -> store document and chunks in Postgres/pgvector
```

## Chunking Strategy

Document text is chunked with the default `paragraph_aware` strategy.

Current settings:

| Setting | Value |
| --- | --- |
| Strategy | `paragraph_aware` |
| Chunk size | 1000 characters |
| Overlap | 150 characters |

The paragraph-aware strategy keeps paragraphs together when they fit within the chunk size. If a paragraph is longer than the configured chunk size, it is split by sentences with overlap. The older fixed-size character chunking behavior is still available in code as the `fixed` strategy.

Chat:

```text
POST /chat/sessions
  -> create a persisted chat session

GET /chat/sessions
  -> list chat sessions ordered by most recently updated

GET /chat/sessions/{session_id}/messages
  -> load messages for a selected session

DELETE /chat/sessions/{session_id}
  -> delete a chat session and its messages

POST /chat
  -> save user message
  -> generate query embedding
  -> search similar chunks in pgvector
  -> build RAG context and prompt
  -> generate answer with llama3.2
  -> save assistant message
  -> return answer with citations

POST /chat/stream
  -> save user message
  -> generate query embedding
  -> search similar chunks in pgvector
  -> build RAG context and prompt
  -> stream the llama3.2 answer as plain text
  -> save assistant message after streaming completes
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
    "top_k": 3,
    "document_id": null,
    "filename": null
  }' | jq
```

## Chat Sessions

Create a chat session before calling `/chat` or `/chat/stream`:

```bash
curl -s -X POST "http://localhost:8000/chat/sessions" | jq
```

List sessions:

```bash
curl -s -X GET "http://localhost:8000/chat/sessions" | jq
```

Load messages for a session:

```bash
curl -s -X GET "http://localhost:8000/chat/sessions/{session_id}/messages" | jq
```

Delete a session and its messages:

```bash
curl -s -X DELETE "http://localhost:8000/chat/sessions/{session_id}" | jq
```

## Chat

```bash
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the story about?",
    "session_id": "{session_id}",
    "top_k": 3,
    "document_id": null,
    "filename": null
  }' | jq
```

## Chat Stream

Use `/chat/stream` when the UI should render the answer as it is generated. The response is streamed as `text/plain` and does not include citations in the response body.

```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the story about?",
    "session_id": "{session_id}",
    "top_k": 3,
    "document_id": null,
    "filename": null
  }'
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
