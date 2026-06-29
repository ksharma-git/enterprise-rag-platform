# RAG Architecture: Enterprise RAG Platform

This document describes the architecture and request flow for the Enterprise RAG Platform.

The platform supports:

- Document upload
- Text extraction
- Text chunking
- Embedding generation
- PostgreSQL + pgvector storage
- Vector search
- Prompt construction
- Ollama `llama3.2` response generation
- Citations

## High-Level Architecture

```text
               ┌────────────────────┐
               │ Streamlit Frontend  │
               │ frontend/app.py     │
               └─────────┬──────────┘
                         │ HTTP
                         v
               ┌────────────────────┐
               │ FastAPI Backend     │
               │ backend/app/main.py │
               └─────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        v                v                v
┌──────────────┐ ┌────────────────┐ ┌────────────────┐
│ API Routes   │ │ Services        │ │ Repositories   │
│ app/api/     │ │ app/services/   │ │ app/repos/     │
└──────┬───────┘ └───────┬────────┘ └───────┬────────┘
       │                 │                  │
       │                 v                  v
       │        ┌────────────────┐ ┌──────────────────┐
       │        │ Ollama          │ │ PostgreSQL        │
       │        │ embeddings + LLM│ │ pgvector          │
       │        └────────────────┘ └──────────────────┘
       │
       v
┌────────────────┐
│ JSON Response   │
└────────────────┘
```

## Folder Structure

```text
enterprise-rag-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   └── retrieval_service.py
│   │   ├── repositories/
│   │   │   ├── document_repository.py
│   │   │   └── chunk_repository.py
│   │   ├── utils/
│   │   │   └── file_store.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   └── requirements.txt
├── db/
│   └── schema.sql
├── frontend/
│   ├── app.py
│   └── requirements.txt
└── docker-compose.yml
```

## Component Responsibilities

| Component | Responsibility |
| --- | --- |
| `frontend/app.py` | Minimal Streamlit UI for upload, chat, documents, chunks, delete |
| `app/main.py` | Creates the FastAPI app and registers routers |
| `app/api/health.py` | Health endpoint |
| `app/api/documents.py` | Document, chunk, upload, search API routes |
| `app/api/chat.py` | Chat API route |
| `app/services/document_service.py` | Upload workflow, extraction, chunking, document listing, delete |
| `app/services/embedding_service.py` | Calls Ollama embedding API |
| `app/services/retrieval_service.py` | Vector search workflow, context building, prompt building, chat workflow |
| `app/services/llm_service.py` | Calls Ollama generate API with `llama3.2` |
| `app/repositories/document_repository.py` | Document database operations |
| `app/repositories/chunk_repository.py` | Chunk database operations and pgvector similarity search |
| `app/utils/file_store.py` | Saves uploaded files locally |
| `app/models.py` | SQLAlchemy models |
| `app/schemas.py` | Request schemas |
| `db/schema.sql` | Database schema and vector index |

## Runtime Dependencies

```text
Frontend: Streamlit
Backend: FastAPI
Database: PostgreSQL 16 + pgvector
Embedding model: nomic-embed-text
LLM: llama3.2
Model runtime: Ollama
```

## API Overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/documents/upload` | Upload and ingest a document |
| `GET` | `/documents` | List uploaded documents |
| `DELETE` | `/documents/{document_id}` | Delete a document and its chunks |
| `GET` | `/chunks` | List stored chunks |
| `POST` | `/search` | Vector search over chunks |
| `POST` | `/chat` | RAG chat answer with citations |

## Document Upload Flow

When a user uploads a document, the platform stores the file, extracts text, chunks the text, embeds each chunk, and stores everything in PostgreSQL.

```text
POST /documents/upload
        |
        v
api/documents.py
        |
        v
document_service.upload_document()
        |
        +--> validate_file_extension()
        |
        +--> file_store.save_uploaded_file()
        |
        +--> extract_text_from_file()
        |
        +--> chunk_text()
        |
        +--> embedding_service.generate_embedding()
        |
        +--> document_repository.save_document()
        |
        +--> chunk_repository.save_document_chunks()
        |
        v
JSON response with document metadata and chunk count
```

### Upload Sequence Diagram

```text
User
 |
 | uploads PDF/TXT/MD
 v
Streamlit Frontend
 |
 | POST /documents/upload
 v
FastAPI documents route
 |
 | calls upload_document_service
 v
Document Service
 |----------------------------------+
 | validate file extension          |
 | save file to uploads/            |
 | extract text                     |
 | split text into chunks           |
 +----------------------------------+
 |
 | for each chunk
 v
Embedding Service
 |
 | POST http://localhost:11434/api/embeddings
 v
Ollama nomic-embed-text
 |
 | embedding vector
 v
Document Service
 |
 | save document + chunks
 v
PostgreSQL + pgvector
 |
 | success
 v
FastAPI -> Streamlit -> User
```

## Text Extraction

Text extraction happens in `document_service.extract_text_from_file()`.

| File Type | Extraction Method |
| --- | --- |
| `.txt` | Read text directly |
| `.md` | Read text directly |
| `.pdf` | Use `pypdf.PdfReader` |

Unsupported file types return a `400` error.

## Chunking

Chunking happens in `document_service.chunk_text()`.

Current settings:

| Setting | Value |
| --- | ---: |
| Chunk size | 1000 characters |
| Overlap | 150 characters |

```text
Document text
   |
   +-- chunk 0: chars 0-1000
   +-- chunk 1: chars 850-1850
   +-- chunk 2: chars 1700-2700
```

Overlap helps preserve context across chunk boundaries.

## Embedding Generation

Embeddings are generated in `embedding_service.generate_embedding()`.

```text
chunk_text
   |
   v
POST /api/embeddings
model: nomic-embed-text
   |
   v
768-dimensional vector
```

The project expects embeddings with 768 dimensions.

## PostgreSQL + pgvector Storage

The database stores documents and document chunks.

```text
documents
├── id
├── filename
├── source_type
├── uploaded_by
└── created_at

document_chunks
├── id
├── document_id
├── chunk_text
├── chunk_index
├── embedding VECTOR(768)
├── chunk_metadata
└── created_at
```

Relationship:

```text
documents.id 1 ──── * document_chunks.document_id
```

`document_chunks.document_id` uses `ON DELETE CASCADE`, so deleting a document deletes its chunks.

## Vector Index

The schema defines an IVFFlat index:

```sql
CREATE INDEX document_chunks_embedding_idx
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

Purpose:

| Part | Meaning |
| --- | --- |
| `ivfflat` | Approximate nearest neighbor index |
| `vector_cosine_ops` | Use cosine distance |
| `lists = 100` | Number of vector clusters |

## Search Flow

The `/search` endpoint returns relevant chunks but does not ask the LLM to generate an answer.

```text
POST /search
        |
        v
api/documents.py
        |
        v
retrieval_service.search_documents()
        |
        +--> generate query embedding
        |
        +--> chunk_repository.search_similar_chunks()
        |
        v
Top matching chunks
```

Search SQL uses pgvector distance:

```sql
dc.embedding <=> CAST(:query_embedding AS vector) AS distance
```

Lower distance means a closer semantic match.

## Chat Flow

The `/chat` endpoint performs the full RAG flow.

```text
POST /chat
   |
   v
api/chat.py
   |
   v
retrieval_service.chat()
   |
   +--> generate query embedding
   |
   +--> search similar chunks in pgvector
   |
   +--> build context from chunks
   |
   +--> build prompt
   |
   +--> ask llama3.2 through Ollama
   |
   +--> build citations
   |
   v
Answer + citations
```

### Chat Sequence Diagram

```text
User
 |
 | asks question
 v
Streamlit Frontend
 |
 | POST /chat
 v
FastAPI chat route
 |
 | calls chat_service
 v
Retrieval Service
 |
 | generate query embedding
 v
Embedding Service
 |
 | POST /api/embeddings
 v
Ollama nomic-embed-text
 |
 | query vector
 v
Retrieval Service
 |
 | vector search
 v
PostgreSQL + pgvector
 |
 | top_k chunks
 v
Retrieval Service
 |
 | build context
 | build prompt
 v
LLM Service
 |
 | POST /api/generate
 v
Ollama llama3.2
 |
 | generated answer
 v
Retrieval Service
 |
 | attach citations
 v
FastAPI -> Streamlit -> User
```

## Prompt Construction

Prompt construction happens in `retrieval_service.build_prompt()`.

The prompt instructs the model:

```text
You are an enterprise knowledge assistant.

Answer ONLY using the provided context.

If the answer cannot be found, say:
"I couldn't find that information in the uploaded documents."

Context:
{retrieved_chunks}

Question:
{user_question}
```

This reduces hallucinations by telling the model to answer only from retrieved chunks.

## Context Construction

Context is built from retrieved chunks:

```text
Document: handbook.pdf

Chunk 3

Password reset instructions...
```

Multiple chunks are joined together and sent to the LLM.

## LLM Response Generation

The LLM call happens in `llm_service.ask_llama()`.

```text
Prompt
  |
  v
POST http://localhost:11434/api/generate
model: llama3.2
stream: false
temperature: 0.2
  |
  v
Answer text
```

Low temperature makes responses more deterministic.

## Citations

The chat response includes citations for each retrieved chunk.

Example:

```json
{
  "query": "What is the policy?",
  "answer": "The policy says...",
  "citations": [
    {
      "chunk_id": "chunk-uuid",
      "document_id": "document-uuid",
      "filename": "policy.pdf",
      "chunk_index": 2,
      "distance": 0.18
    }
  ]
}
```

Citations help users verify where the answer came from.

## Delete Document Flow

```text
DELETE /documents/{document_id}
        |
        v
api/documents.py
        |
        v
document_service.delete_document()
        |
        v
document_repository.delete_document()
        |
        v
PostgreSQL deletes document
        |
        v
document_chunks are deleted by ON DELETE CASCADE
```

## API Flow Summary

| Endpoint | API Module | Service | Repository |
| --- | --- | --- | --- |
| `GET /` | `api/health.py` | None | None |
| `POST /documents/upload` | `api/documents.py` | `document_service.upload_document()` | `save_document()`, `save_document_chunks()` |
| `GET /documents` | `api/documents.py` | `document_service.list_documents()` | `list_documents()` |
| `DELETE /documents/{id}` | `api/documents.py` | `document_service.delete_document()` | `delete_document()` |
| `GET /chunks` | `api/documents.py` | `document_service.list_chunks()` | `list_chunks()` |
| `POST /search` | `api/documents.py` | `retrieval_service.search_documents()` | `search_similar_chunks()` |
| `POST /chat` | `api/chat.py` | `retrieval_service.chat()` | `search_similar_chunks()` |

## Data Flow Summary

```text
Upload path:
File -> Text -> Chunks -> Embeddings -> PostgreSQL/pgvector

Chat path:
Question -> Query embedding -> Vector search -> Context -> Prompt -> llama3.2 -> Answer + citations
```

## Key Design Choices

| Decision | Reason |
| --- | --- |
| FastAPI backend | Simple API framework for Python |
| Streamlit frontend | Minimal UI with little code |
| PostgreSQL + pgvector | Store relational data and vectors together |
| Ollama local models | Run embeddings and LLM locally |
| Separate services | Keep API routes thin |
| Separate repositories | Keep DB access isolated |
| Citations | Make answers traceable |
| Chunk metadata | Support filtering and debugging later |

## Current Limitations

| Limitation | Future Improvement |
| --- | --- |
| `/chunks` returns all chunks | Add pagination |
| No authentication | Add users and permissions |
| No reranking | Add reranker after vector search |
| No similarity threshold | Reject weak retrieval results |
| No migration tool | Add Alembic |
| Local file storage only | Add object storage for production |

## Production Notes

For enterprise use, add:

- Authentication and authorization
- Per-document access control
- Audit logging
- Pagination for list endpoints
- Schema migrations
- Observability for latency and errors
- Retrieval quality evaluation
- Backup and restore strategy
- Secure secret management
