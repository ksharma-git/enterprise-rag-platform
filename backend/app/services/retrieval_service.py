from sqlalchemy.orm import Session

from app.repositories.chunk_repository import search_similar_chunks, keyword_search_chunks
from app.services.embedding_service import generate_embedding
from app.services.llm_service import ask_llama
from app.services.vector_store_service import hybrid_merge


def build_context(chunks):
    context = []

    for chunk in chunks:
        context.append(
            f"""
Document: {chunk["filename"]}

Chunk {chunk["chunk_index"]}

{chunk["chunk_text"]}
"""
        )

    return "\n\n".join(context)

def build_prompt(question, context):

    return f"""
You are an enterprise knowledge assistant.

Answer ONLY using the provided context.

If the answer cannot be found, say:

"I couldn't find that information in the uploaded documents."

Context:

{context}

Question:

{question}
"""


def search_documents(query: str, top_k: int, db: Session):
    query_embedding = generate_embedding(query)

    vector_results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    keyword_results = keyword_search_chunks(
        db=db,
        query=query,
        top_k=top_k,
    )

    results = hybrid_merge(
        vector_results=vector_results,
        keyword_results=keyword_results,
        top_k=top_k,
    )

    return {
        "query": query,
        "top_k": top_k,
        "results": [
            {
                "chunk_id": row["chunk_id"],
                "document_id": str(row["document_id"]),
                "filename": row["filename"],
                "chunk_index": row["chunk_index"],
                "chunk_text": row["chunk_text"],
                "hybrid_score": row["hybrid_score"],
                "vector_score": row["vector_score"],
                "keyword_score": row["keyword_score"],
                "chunk_metadata": row["chunk_metadata"],
            }
            for row in results
        ],
    }


def chat(query: str, top_k: int, db: Session):
    query_embedding = generate_embedding(query)

    received_chunks = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
    )

    if not received_chunks:
        return {
            "question": query,
            "answer": "I could not find any relevant information in the uploaded documents.",
            "citations": [],
        }

    context = build_context(received_chunks)

    prompt = build_prompt(query, context)

    answer = ask_llama(prompt)

    citations = [
        {
            "chunk_id": str(chunk["id"]),
            "document_id": str(chunk["document_id"]),
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "distance": float(chunk["distance"]),
        }
        for chunk in received_chunks
    ]

    return {
        "query": query,
        "answer": answer,
        "citations": citations,
    }
