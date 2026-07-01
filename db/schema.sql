CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    source_type TEXT DEFAULT 'upload',
    uploaded_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INT NOT NULL,
    embedding VECTOR(768),
    chunk_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);


ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS search_vector tsvector;

UPDATE document_chunks
SET search_vector = to_tsvector('english', chunk_text);

CREATE INDEX IF NOT EXISTS document_chunks_search_idx
ON document_chunks
USING GIN (search_vector);
