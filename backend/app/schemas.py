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
