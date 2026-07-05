from sqlalchemy.orm import Session

from app.repositories.chat_repository import create_chat_session as create_session
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
