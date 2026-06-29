# Technical Insights: Enterprise RAG Platform

This guide explains the main AI and RAG concepts used in the Enterprise RAG Platform.

## What This Project Does

The platform lets users upload documents, stores searchable chunks of those documents, and answers questions using only the most relevant document content.

```text
User uploads file
      |
      v
Extract text from PDF/TXT/MD
      |
      v
Split text into chunks
      |
      v
Create embeddings with nomic-embed-text
      |
      v
Store chunks + vectors in PostgreSQL + pgvector
      |
      v
User asks a question
      |
      v
Find similar chunks using vector search
      |
      v
Send context + question to llama3.2
      |
      v
Return answer with citations
```

## AI Basics

Artificial intelligence in this project has two main jobs:

| Job | Tool | Purpose |
| --- | --- | --- |
| Understand meaning | Embedding model | Converts text into vectors |
| Generate answer | LLM | Writes a natural language response |

The project uses:

| Component | Current Choice |
| --- | --- |
| Embedding model | `nomic-embed-text` |
| LLM | `llama3.2` |
| Vector database | PostgreSQL + pgvector |
| Backend | FastAPI |
| Frontend | Streamlit |

## What Is RAG?

RAG means **Retrieval-Augmented Generation**.

Instead of asking an LLM to answer from memory only, RAG first retrieves relevant information from your own documents, then asks the LLM to answer using that information.

```text
Without RAG:
Question -> LLM -> Answer from model memory

With RAG:
Question -> Retrieve relevant document chunks -> LLM -> Grounded answer
```

Why RAG is useful:

| Problem | How RAG Helps |
| --- | --- |
| LLM does not know private company documents | Documents are uploaded and searched locally |
| LLM can hallucinate | Prompt says to answer only from retrieved context |
| Documents change often | Update documents without retraining the LLM |
| Need citations | Return chunks used for the answer |

## Embeddings

Embeddings are lists of numbers that represent the meaning of text.

Example:

```text
"How do I reset my password?"
        |
        v
[0.12, -0.43, 0.88, ...]
```

Similar text gets similar vectors.

| Text | Meaning |
| --- | --- |
| "How do I reset my password?" | Account recovery |
| "I forgot my login password" | Account recovery |
| "What is the refund policy?" | Billing/refunds |

The first two should be close together in vector space. The refund question should be farther away.

## `embedding VECTOR(768)`

In this project, document chunks are stored with an embedding column:

```sql
embedding VECTOR(768)
```

Meaning:

| Part | Meaning |
| --- | --- |
| `VECTOR` | Data type from pgvector |
| `768` | Number of dimensions in each vector |
| `embedding` | Numeric representation of a text chunk |

The dimension must match the embedding model.

| Embedding Model | Dimensions |
| --- | ---: |
| `nomic-embed-text` | 768 |
| `BAAI/bge-base-en-v1.5` | 768 |
| `text-embedding-3-small` | 1536 |

If the model returns 768 numbers, the database column must be `VECTOR(768)`.

## Embedding Models vs LLMs

Embedding models and LLMs are different.

| Feature | Embedding Model | LLM |
| --- | --- | --- |
| Example | `nomic-embed-text` | `llama3.2` |
| Input | Text | Prompt/context |
| Output | Vector/list of numbers | Text answer |
| Main job | Similarity search | Language generation |
| Used during upload | Yes | No |
| Used during chat | Yes, for query embedding | Yes, for final answer |

Simple rule:

```text
Embedding model finds relevant text.
LLM writes the answer.
```

## Chunking

LLMs and embedding models work better when long documents are split into smaller pieces called chunks.

```text
Large document
  |
  +-- chunk 0
  +-- chunk 1
  +-- chunk 2
  +-- chunk 3
```

This project uses:

| Setting | Value |
| --- | ---: |
| Chunk size | 1000 characters |
| Chunk overlap | 150 characters |

Overlap means the end of one chunk is repeated at the start of the next chunk. This helps avoid losing context at chunk boundaries.

```text
Chunk 1: [...............important sentence starts here]
Chunk 2:          [important sentence starts here...............]
```

Good chunking improves retrieval quality. Bad chunking can cause incomplete or irrelevant answers.

## Vector Databases

A vector database stores embeddings and searches for similar vectors quickly.

This project uses PostgreSQL with the pgvector extension.

```text
document_chunks table

id | document_id | chunk_text | embedding
---|-------------|------------|----------------
1  | doc-1       | text...    | [0.1, 0.2, ...]
2  | doc-1       | text...    | [0.4, 0.7, ...]
3  | doc-2       | text...    | [0.9, 0.3, ...]
```

When the user asks a question:

```text
Question -> embedding -> compare with chunk embeddings -> return closest chunks
```

## pgvector

pgvector adds vector support to PostgreSQL.

It provides:

| Feature | Purpose |
| --- | --- |
| `VECTOR(n)` type | Store embeddings |
| Distance operators | Compare vectors |
| Vector indexes | Speed up search |

Example schema:

```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INT NOT NULL,
    embedding VECTOR(768),
    chunk_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Cosine Similarity

Cosine similarity compares the direction of two vectors. For text embeddings, direction usually matters more than vector size.

```text
Same meaning      -> small angle -> high similarity
Different meaning -> large angle -> low similarity
```

In pgvector, cosine distance is commonly used with:

```sql
embedding <=> query_embedding
```

Lower distance means more similar.

| Distance | Meaning |
| ---: | --- |
| 0.05 | Very similar |
| 0.25 | Somewhat related |
| 0.80 | Not very related |

## Vector Indexes

Without an index, PostgreSQL may compare the query vector with every stored vector. That is slow when there are many chunks.

Vector indexes make search faster.

### IVFFlat

IVFFlat groups vectors into clusters.

```text
All vectors
  |
  +-- cluster 1
  +-- cluster 2
  +-- cluster 3
```

At query time, PostgreSQL searches the most relevant clusters instead of all vectors.

Current project index:

```sql
CREATE INDEX document_chunks_embedding_idx
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

| Setting | Meaning |
| --- | --- |
| `ivfflat` | Approximate nearest neighbor index |
| `vector_cosine_ops` | Use cosine distance |
| `lists = 100` | Number of vector clusters |

### HNSW

HNSW means **Hierarchical Navigable Small World**. It builds a graph of vectors so similar vectors can be found quickly.

```text
Query vector
   |
   v
Nearest graph nodes
   |
   v
Best matching chunks
```

Example:

```sql
CREATE INDEX document_chunks_embedding_idx
ON document_chunks
USING hnsw (embedding vector_cosine_ops);
```

### IVFFlat vs HNSW

| Feature | IVFFlat | HNSW |
| --- | --- | --- |
| Build speed | Faster | Slower |
| Query speed | Fast | Very fast |
| Recall/accuracy | Good | Excellent |
| Memory usage | Lower | Higher |
| Needs training/analyze | More sensitive | Less sensitive |
| Best for | Simple/medium datasets | Production RAG |

Recommended path:

| Stage | Index |
| --- | --- |
| Learning/local development | IVFFlat |
| Production with many chunks | HNSW |

## Retrieval

Retrieval is the process of finding the most relevant chunks for a user question.

```text
User question
   |
   v
Generate query embedding
   |
   v
Search document_chunks by vector distance
   |
   v
Return top_k chunks
```

Example search result:

| chunk_index | filename | distance | preview |
| ---: | --- | ---: | --- |
| 4 | policy.pdf | 0.12 | Password reset requires... |
| 7 | handbook.pdf | 0.18 | Users can reset credentials... |
| 2 | faq.md | 0.22 | Login help is available... |

The backend then sends those chunks to the LLM as context.

## Prompt Engineering

Prompt engineering means writing instructions that guide the LLM.

For enterprise RAG, the prompt should be strict:

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

Good RAG prompts:

| Rule | Why It Matters |
| --- | --- |
| Use only provided context | Reduces hallucination |
| Give fallback answer | Avoids fake answers |
| Include citations | Helps users verify |
| Keep retrieved context focused | Improves answer quality |

## Hallucination Prevention

Hallucination means the model gives an answer that sounds correct but is not supported by the documents.

Ways this project reduces hallucination:

| Technique | How It Helps |
| --- | --- |
| Retrieve relevant chunks | Gives the LLM source material |
| Prompt says answer only from context | Limits unsupported answers |
| Return citations | Lets users inspect sources |
| Use top_k chunks | Avoids overloading prompt with irrelevant text |

Extra improvements for later:

| Improvement | Purpose |
| --- | --- |
| Similarity threshold | Reject weak matches |
| Reranking | Improve chunk ordering |
| Document filters | Search only selected documents |
| Source previews | Make citations easier to inspect |
| Evaluation set | Test answer quality over time |

## Enterprise RAG Best Practices

### Data Ingestion

| Practice | Reason |
| --- | --- |
| Validate file type | Avoid unsupported files |
| Store original filename | Helps citations |
| Track uploader | Helps auditing |
| Keep chunk metadata | Enables filtering later |
| Delete chunks when documents are deleted | Prevents stale retrieval |

### Chunking

| Practice | Reason |
| --- | --- |
| Avoid chunks that are too small | They lose context |
| Avoid chunks that are too large | They reduce retrieval precision |
| Use overlap | Preserves boundary context |
| Keep chunk index | Maintains document order |

### Retrieval

| Practice | Reason |
| --- | --- |
| Tune `top_k` | Balances context quality and prompt size |
| Use cosine distance for text | Common for semantic search |
| Add metadata filters later | Improves enterprise use cases |
| Monitor low-quality matches | Helps improve chunking/indexing |

### Security and Governance

| Practice | Reason |
| --- | --- |
| Do not commit `.env` files | Protects secrets |
| Add authentication later | Controls access |
| Track users and uploads | Enables audit logs |
| Enforce document permissions | Prevents data leaks |
| Log retrieval sources | Helps compliance and debugging |

### Operations

| Practice | Reason |
| --- | --- |
| Use migrations | Keeps schema changes controlled |
| Add health checks | Helps deployment |
| Add tests for chunking/retrieval | Prevents regressions |
| Monitor latency | Embeddings and LLM calls can be slow |
| Add pagination | Prevents large list endpoints from slowing down |

## Current Project Architecture

```text
enterprise-rag-platform/
├── backend/
│   ├── app/
│   │   ├── api/              FastAPI route handlers
│   │   ├── services/         Business workflows and AI integrations
│   │   ├── repositories/     Database operations
│   │   ├── utils/            File helper functions
│   │   ├── config.py         App constants and environment values
│   │   ├── database.py       SQLAlchemy engine/session
│   │   ├── models.py         SQLAlchemy models
│   │   ├── schemas.py        Request schemas
│   │   └── main.py           FastAPI app setup
│   └── requirements.txt
├── db/
│   └── schema.sql
├── frontend/
│   ├── app.py                Streamlit UI
│   └── requirements.txt
└── docker-compose.yml
```

## Current Project Configuration

| Area | Value |
| --- | --- |
| Database | PostgreSQL 16 |
| Vector extension | pgvector |
| Embedding model | `nomic-embed-text` |
| Embedding dimension | 768 |
| LLM | `llama3.2` |
| Distance metric | Cosine distance |
| Current index | IVFFlat |
| Backend | FastAPI |
| Frontend | Streamlit |

## End-to-End Example

### Upload

```text
User uploads handbook.pdf
  -> backend saves file
  -> extracts text
  -> splits text into chunks
  -> creates embedding for each chunk
  -> stores chunks in document_chunks
```

### Chat

```text
User asks:
"How do I reset my password?"

Backend:
  -> embeds the question
  -> finds similar chunks
  -> builds context
  -> asks llama3.2

Answer:
"According to the uploaded handbook, users can reset their password..."
```

## Quick Glossary

| Term | Meaning |
| --- | --- |
| AI | Software that performs tasks that seem intelligent |
| LLM | Large language model that generates text |
| Embedding | Vector representation of meaning |
| Vector | List of numbers |
| Chunk | Smaller piece of a document |
| RAG | Retrieval-Augmented Generation |
| Retrieval | Finding relevant document chunks |
| pgvector | PostgreSQL extension for vectors |
| Cosine similarity | Measures semantic closeness between vectors |
| Citation | Reference to the retrieved source chunk |
| Hallucination | Unsupported or invented model output |

## Simple Mental Model

```text
Documents are the knowledge.
Embeddings are the map.
Vector search finds the closest location on the map.
The LLM turns the found knowledge into an answer.
```
