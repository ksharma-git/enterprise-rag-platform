from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.chat_repository import create_chat_session as create_session
from app.repositories.chat_repository import delete_chat_session as delete_session
from app.repositories.chat_repository import get_session_messages, list_chat_sessions

def create_chat_session(db: Session):
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

def delete_chat_session(
    db: Session, session_id: str
):
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid chat session id")

    session = delete_session(db, session_uuid)

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return {
        "message": "Chat session deleted successfully",
        "session_id": session_id,
    }
