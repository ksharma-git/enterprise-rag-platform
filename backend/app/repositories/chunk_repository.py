import os

from sqlalchemy import text
from sqlalchemy.orm import Session

def save_document_chunks(db: Session, chunks: list):
    db.add_all(chunks)
    db.commit()

    for chunk in chunks:
        db.refresh(chunk)

    return chunks


def list_chunks(db: Session, document_model, chunk_model):
    return (
        db.query(chunk_model, document_model.filename)
        .join(document_model, document_model.id == chunk_model.document_id)
        .order_by(chunk_model.created_at.desc())
        .all()
    )


def search_similar_chunks(db: Session, query_embedding: list[float], top_k: int = 5):
    sql = text("""
        SELECT
            dc.id,
            dc.document_id,
            d.filename,
            dc.chunk_text,
            dc.chunk_index,
            dc.chunk_metadata,
            dc.embedding <=> CAST(:query_embedding AS vector) AS distance
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE dc.embedding IS NOT NULL
        ORDER BY dc.embedding <=> CAST(:query_embedding AS vector)
        LIMIT :top_k
    """)

    result = db.execute(
        sql,
        {
            "query_embedding": query_embedding,
            "top_k": top_k,
        },
    )

    return result.mappings().all()

def update_chunk_search_vector(db: Session) -> None:
    db.execute(
        text("""
            UPDATE document_chunks
            SET search_vector = to_tsvector('english', chunk_text)
            WHERE search_vector IS NULL
        """)
    )
    db.commit()

def keyword_search_chunks(db: Session, query: str, top_k: int = 5):
    sql = text("""
           SELECT
               dc.id,
               dc.document_id,
               d.filename,
               dc.chunk_text,
               dc.chunk_index,
               dc.chunk_metadata,
               ts_rank(dc.search_vector, plainto_tsquery('english', :query)) AS keyword_score
           FROM document_chunks dc
           JOIN documents d ON d.id = dc.document_id
           WHERE dc.search_vector @@ plainto_tsquery('english', :query)
           ORDER BY keyword_score DESC
           LIMIT :top_k
       """)

    result = db.execute(
        sql,
        {
            "query": query,
            "top_k": top_k,
        },
    )
    return result.mappings().all()
