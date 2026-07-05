from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[str] = None
    filename: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[str] = None
    filename: Optional[str] = None
    session_id: str

class ChatSessionResponse(BaseModel):
    session_id: str
    title: str

class ChatMessageResponse(BaseModel):
    content: str
    role: str
    citations: list = []
    created_at: str
