from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.repositories.chunk_repository import search_similar_chunks, keyword_search_chunks
from app.repositories.chat_repository import get_chat_session, get_recent_messages, save_chat_message
from app.services.embedding_service import generate_embedding
from app.services.hybrid_search_service import hybrid_merge
from app.services.llm_service import ask_llama, ask_llama_stream

from app.models import ChatSession
from app.config import CHAT_ROLE_USER, CHAT_ROLE_ASSISTANT

NO_CONTEXT_ANSWER = "I could not find any relevant information in the uploaded documents."

def build_history_text(messages) -> str:
    if not messages:
        return "No previous conversation."

    history_lines = []

    for message in messages:
        role = "User" if message.role == "user" else "Assistant"
        history_lines.append(f"{role}: {message.content}")

    return "\n".join(history_lines)

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

def build_prompt(
    question: str,
    context: str,
    chat_history=None,
) -> str:
    history_text = build_history_text(chat_history or [])

    return f"""
You are an Enterprise Knowledge Assistant.

Use the retrieved context as the source of truth.
Use conversation history only to understand follow-up questions.
If the answer is not in the retrieved context, say you could not find it in the uploaded documents.

Conversation history:
{history_text}

Retrieved context:
{context}

Current question:
{question}

Answer:
"""


def search_documents(query: str, top_k: int, db: Session, document_id=None, filename=None):
    results = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
        db=db,
        document_id=document_id,
        filename=filename,
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


def retrieve_relevant_chunks(query: str, top_k: int, db: Session, document_id=None, filename=None):
    query_embedding = generate_embedding(query)

    vector_results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        document_id=document_id,
        filename=filename,
        top_k=top_k,
    )

    keyword_results = keyword_search_chunks(
        db=db,
        query=query,
        document_id=document_id,
        filename=filename,
        top_k=top_k,
    )

    return hybrid_merge(
        vector_results=vector_results,
        keyword_results=keyword_results,
        top_k=top_k,
    )


def chat(query: str, top_k: int, db: Session, session_id: str, document_id=None, filename=None):
    chat_session = get_chat_session_or_throw(db, session_id)
    save_chat_message(db, session_id, CHAT_ROLE_USER, query)
    recent_messages = get_recent_messages(
        db=db,
        session_id=session_id,
        limit=6,
    )
    recent_messages = list(reversed(recent_messages))

    received_chunks = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
        db=db,
        document_id=document_id,
        filename=filename,
    )

    if not received_chunks:
        save_chat_message(db, session_id, CHAT_ROLE_ASSISTANT, NO_CONTEXT_ANSWER, [])
        return {
            "session_id": str(chat_session.id),
            "question": query,
            "answer": NO_CONTEXT_ANSWER,
            "citations": [],
        }

    context = build_context(received_chunks)

    prompt = build_prompt(query, context, recent_messages)

    answer = ask_llama(prompt)

    citations = build_citations(received_chunks)

    save_chat_message(db, session_id, CHAT_ROLE_ASSISTANT, answer, citations)

    return {
        "session_id": str(chat_session.id),
        "query": query,
        "answer": answer,
        "citations": citations,
    }

def chat_stream(query: str, top_k: int, db: Session, session_id: str, document_id=None, filename=None):
    chat_session = get_chat_session_or_throw(db, session_id)

    save_chat_message(db, session_id, CHAT_ROLE_USER, query)

    recent_messages = get_recent_messages(
        db=db,
        session_id=session_id,
        limit=6,
    )
    recent_messages = list(reversed(recent_messages))

    received_chunks = retrieve_relevant_chunks(
        query=query,
        top_k=top_k,
        db=db,
        document_id=document_id,
        filename=filename,
    )

    if not received_chunks:
        save_chat_message(
            db,
            chat_session.id,
            CHAT_ROLE_ASSISTANT,
            NO_CONTEXT_ANSWER,
            [],
        )

        return StreamingResponse(
            iter([NO_CONTEXT_ANSWER]),
            media_type="text/plain",
        )

    context = build_context(received_chunks)

    prompt = build_prompt(query, context, recent_messages)

    citations = build_citations(received_chunks)

    def token_generator():
        full_answer = ""
        if not received_chunks:
            yield NO_CONTEXT_ANSWER
            return

        for token in ask_llama_stream(prompt):
            full_answer += token
            yield token

        save_chat_message(db, session_id, CHAT_ROLE_ASSISTANT, full_answer, citations)

    return StreamingResponse(
        token_generator(),
        media_type="text/plain",
    )

def get_chat_session_or_throw(
        db: Session, session_id: str,
) -> ChatSession:
    session = get_chat_session(db, session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chat session '{session_id}' not found.",
        )

    return session

def build_citations(chunks):
    return [
        {
            "chunk_id": str(chunk["chunk_id"]),
            "document_id": str(chunk["document_id"]),
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "vector_score": chunk.get("vector_score"),
            "keyword_score": chunk.get("keyword_score"),
            "hybrid_score": chunk.get("hybrid_score"),
            "distance": float(chunk["distance"]) if chunk.get("distance") is not None else None,
        }
        for chunk in chunks
    ]
