import uuid
from sqlalchemy.orm import Session
from app.models import ChatSession, ChatMessage
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import text

def create_chat_session(db: Session, title: str = "Chat Session"):
    chat_session = ChatSession(title=title)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return chat_session

def list_chat_sessions(db: Session) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

def save_chat_message(
    db: Session,
    session_id,
    role: str,
    content: str,
    citations: list | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        citations=citations or [],
    )

    db.add(message)

    db.execute(
        text("""
            UPDATE chat_sessions
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = :session_id
        """),
        {"session_id": str(session_id)},
    )

    db.commit()
    db.refresh(message)

    return message

def get_session_messages(
    db: Session,
    session_id: str,
) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == uuid.UUID(session_id))
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

def get_chat_session(
    db: Session,
    session_id: str,
) -> ChatSession:
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == uuid.UUID(session_id))
        .first()
    )

def delete_chat_session(
    db: Session,
    session_id,
) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .first()
    )

    if not session:
        return None

    db.delete(session)
    db.commit()

    return session

def get_recent_messages(
    db: Session,
    session_id,
    limit: int,
) -> list[ChatMessage]:
    return  (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
