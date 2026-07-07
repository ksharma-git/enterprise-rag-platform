# Enterprise RAG Platform Demo

This guide walks through a complete portfolio demo of the Enterprise RAG Platform:
Docker startup, Ollama verification, document upload, retrieval, grounded chat,
streaming responses, citations, and hybrid search scores.

## Prerequisites

- Docker Desktop or Docker Engine
- Ollama running locally
- `jq` installed for readable curl output
- Required Ollama models:
  - `llama3.2`
  - `nomic-embed-text`

## 1. Start the App with Docker Compose

From the repository root:

```bash
docker compose up -d --build
```

Verify containers are running:

```bash
docker compose ps
```

Open the apps:

- Streamlit UI: http://localhost:8501
- FastAPI backend: http://localhost:8000

Check the backend health endpoint:

```bash
curl -s http://localhost:8000/ | jq
```

## 2. Verify Ollama Models Are Available

Confirm Ollama is running:

```bash
ollama list
```

If needed, pull the required models:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

The backend container calls Ollama through `host.docker.internal:11434`, so Ollama
must be running on the host machine.

## 3. Upload the Sample Document

The demo document is:

```text
demo/demo-data/enterprise-deployment-playbook.md
```

Upload with curl:

```bash
curl -s -X POST "http://localhost:8000/documents/upload" \
  -F "file=@demo/demo-data/enterprise-deployment-playbook.md" \
  -F "uploaded_by=portfolio-demo" | jq
```

UI flow:

1. Open http://localhost:8501.
2. Select `Documents`.
3. Upload `demo/demo-data/enterprise-deployment-playbook.md`.
4. Click `Upload`.

## 4. Show the Documents Page

In the UI:

1. Open `Documents`.
2. Click `Refresh` in the document library.
3. Show the uploaded `enterprise-deployment-playbook.md` document.

Equivalent API check:

```bash
curl -s "http://localhost:8000/documents" | jq
```

## 5. Show the Chunks Page

In the UI:

1. Open `Chunks`.
2. Click `Load Chunks`.
3. Show that the uploaded document was split into retrievable chunks.

Equivalent API check:

```bash
curl -s "http://localhost:8000/chunks" | jq
```

## 6. Ask Questions in Chat

Create a chat session:

```bash
SESSION_ID="$(
  curl -s -X POST "http://localhost:8000/chat/sessions" | jq -r '.session_id'
)"
echo "$SESSION_ID"
```

Ask a grounded RAG question:

```bash
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"How are applications deployed?\",
    \"session_id\": \"${SESSION_ID}\",
    \"top_k\": 3,
    \"filename\": \"enterprise-deployment-playbook.md\"
  }" | jq
```

UI flow:

1. Open `Chat`.
2. Create or select a chat session.
3. Ask: `How are applications deployed?`
4. Show the grounded answer.

Good follow-up questions:

- `What happens if deployment validation fails?`
- `What does the knowledge assistant use citations for?`
- `What should the on-call engineer review during an incident?`

## 7. Demonstrate Streaming Response

Use the streaming endpoint:

```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What happens if deployment validation fails?\",
    \"session_id\": \"${SESSION_ID}\",
    \"top_k\": 3,
    \"filename\": \"enterprise-deployment-playbook.md\"
  }"
```

UI flow:

1. Open `Chat Stream`.
2. Select the same or a new chat session.
3. Ask: `What happens if deployment validation fails?`
4. Point out that the stream button disables immediately and shows
   `Generating response...` while the answer streams.

## 8. Show Sources Used and Citations

The regular `Chat` endpoint returns citations in the response body:

```bash
curl -s -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What does the knowledge assistant use citations for?\",
    \"session_id\": \"${SESSION_ID}\",
    \"top_k\": 3,
    \"filename\": \"enterprise-deployment-playbook.md\"
  }" | jq '.citations'
```

UI flow:

1. Open `Chat`.
2. Ask: `What does the knowledge assistant use citations for?`
3. Show the `Sources used` section.
4. Expand a source to show filename, chunk ID, chunk index, scores, and chunk text.

## 9. Use Search to Show Hybrid Search Scores

Run hybrid search:

```bash
curl -s -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deployment pipeline security scanning",
    "top_k": 3,
    "filename": "enterprise-deployment-playbook.md"
  }' | jq '.results[] | {
    filename,
    chunk_index,
    hybrid_score,
    vector_score,
    keyword_score,
    preview: (.chunk_text[0:220])
  }'
```

UI flow:

1. Open `Search`.
2. Search for: `deployment pipeline security scanning`.
3. Set `Top K` to `3`.
4. Optionally filter by filename: `enterprise-deployment-playbook.md`.
5. Show `hybrid_score`, `vector_score`, and `keyword_score`.

## Demo Close

Suggested closing points:

- The platform ingests enterprise documents and stores searchable chunks in
  PostgreSQL with pgvector.
- Search combines semantic vector retrieval and keyword matching.
- Chat answers are grounded in retrieved document context.
- Citations make answers auditable.
- Streaming improves perceived responsiveness.
