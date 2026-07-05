from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.repositories.chunk_repository import search_similar_chunks, keyword_search_chunks
from app.repositories.chat_repository import get_chat_session, get_recent_messages, save_chat_message, list_chat_sessions, get_session_messages
from app.repositories.chat_repository import create_chat_session as create_session
from app.services.embedding_service import generate_embedding
from app.services.hybrid_search_service import hybrid_merge
from app.services.llm_service import ask_llama, ask_llama_stream

from app.config import CHAT_ROLE_USER, CHAT_ROLE_ASSISTANT

def create_chat_session(
        db: Session, session_id: str | None,
):
    session = create_session(db)
    return {
        "session_id": str(session.id),
        "title": session.title,
        "created_at": str(session.created_at),
    }

def get_chat_sessions(
    db: Session
):
    sessions = list_chat_sessions(db)
    return [
        {
            "session_id": str(session.id),
            "title": session.title,
            "created_at": str(session.created_at),
            "updated_at": str(session.updated_at),
        }
        for session in sessions
    ]

def get_chat_messages(
    db: Session, session_id: str
):
    messages = get_session_messages(db, session_id)
    return [
        {
            "id": str(message.id),
            "role": message.role,
            "content": message.content,
            "citations": message.citations,
            "created_at": str(message.created_at),
        }
        for message in messages
    ]
