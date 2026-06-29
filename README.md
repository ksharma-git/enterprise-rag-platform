# Enterprise RAG Platform

Enterprise RAG Platform is a local retrieval-augmented generation API for uploading documents, generating embeddings, searching relevant chunks, and answering questions with Ollama.

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

## Database Setup

Start the services defined in `docker-compose.yml`:

```bash
docker compose up -d
```

Enable the `vector` extension in the local Postgres database:

```bash
docker exec -it enterprise-rag-postgres psql -U postgres -d enterprise_rag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

Verify installed extensions:

```bash
docker exec -it enterprise-rag-postgres psql -U postgres -d enterprise_rag -c "\\dx"
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
