from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest
from app.services.retrieval_service import chat as chat_service
from app.services.retrieval_service import chat_stream as chat_stream_service

router = APIRouter()


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    return chat_service(request.query, request.top_k, db, request.document_id, request.filename)


@router.post("/chat/stream")
def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    return chat_stream_service(request.query, request.top_k, db, request.document_id, request.filename)
