from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.session_service import create_chat_session, delete_chat_session, get_chat_sessions, get_chat_messages

router = APIRouter()


@router.post("/chat/sessions")
def create_session(db: Session = Depends(get_db)):
    return create_chat_session(db)


@router.get("/chat/sessions")
def get_sessions(db: Session = Depends(get_db)):
    return get_chat_sessions(db)


@router.get("/chat/sessions/{session_id}/messages")
def get_messages(session_id: str, db: Session = Depends(get_db)):
    return get_chat_messages(db, session_id)


@router.delete("/chat/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    return delete_chat_session(db, session_id)
