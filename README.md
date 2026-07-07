# Enterprise RAG Platform

Enterprise RAG Platform is a local retrieval-augmented generation API for uploading documents, generating embeddings, searching relevant chunks, and answering questions with Ollama.

## Roadmap

### Version 1.0

- Document Upload
- Text Extraction
- Paragraph-aware Chunking
- Embeddings
- PostgreSQL + pgvector
- Vector Search
- Chat
- Streaming Chat UI

### Version 1.1

- Hybrid Search
- Metadata Filtering
- Persisted Chat Sessions
- Chat Session Delete
- Streamed Chat UX Improvements

## Project Structure

```text
enterprise-rag-platform/
├── backend/                 FastAPI application
│   ├── app/                 API, services, database models, and schemas
│   └── README.md            Backend run commands and API examples
├── frontend/                Streamlit frontend
├── docker-compose.yml       Local Postgres with pgvector
└── README.md                Project-level setup
```

Backend organization:

```text
backend/app/
├── api/                     FastAPI routes
├── services/                Business workflows and integrations
├── repositories/            Database operations
├── utils/                   Small helpers
├── config.py                App constants and environment values
├── database.py              Database engine and sessions
├── models.py                SQLAlchemy models
├── schemas.py               Request and response schemas
└── main.py                  FastAPI app setup
```

## Local Setup

Create and activate a local Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

## Docker Compose

Docker Compose starts Postgres, the FastAPI backend, and the Streamlit frontend. On a fresh Postgres volume, `db/schema.sql` initializes the schema, pgvector extension, and indexes.

If the Postgres volume already exists, init scripts will not run again. To recreate the local database from `db/schema.sql`, stop services and remove volumes:

```bash
docker compose down -v
```

Build and start all services:

```bash
docker compose up --build
```

Run all services in the background:

```bash
docker compose up -d --build
```

View running containers:

```bash
docker compose ps
```

View service logs:

```bash
docker compose logs -f
```

Execute a shell inside the backend container:

```bash
docker compose exec backend-rag-app sh
```

Execute a SQL command inside Postgres:

```bash
docker compose exec postgres psql -U postgres -d enterprise_rag
```

Verify installed extensions:

```bash
docker compose exec postgres psql -U postgres -d enterprise_rag -c "\\dx"
```

Stop all services:

```bash
docker compose stop
```

Stop and remove containers:

```bash
docker compose down
```

## Ollama Setup

Install and start Ollama on your local machine:

```bash
ollama serve
```

Pull the models required by the application:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

Required local models:

- `llama3.2` - answer generation
- `nomic-embed-text` - embeddings

## Backend

See `backend/README.md` for API run commands, upload examples, search/chat examples, and DB verification queries.

## Frontend

Run the Streamlit frontend:

```bash
streamlit run frontend/app.py
```

The Streamlit UI includes a compact chat-session sidebar for both `Chat` and `Chat Stream`.
Session rows are horizontal list items with the title on the left and a trash action on
the right. Deleting a session requires confirmation.

`Chat Stream` disables the composer immediately after submit, shows a
`Generating response...` state while the backend streams, and re-enables controls after
the response completes or fails. Both chat pages auto-scroll when new messages arrive.

When validating frontend changes in Docker, rebuild the frontend image because
`frontend/app.py` is copied into the image at build time:

```bash
docker compose up -d --build frontend-ui-app
```
