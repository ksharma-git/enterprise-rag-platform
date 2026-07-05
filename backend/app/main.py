from pathlib import Path

from fastapi import FastAPI

from app.api import chat, documents, health, session

app = FastAPI(title="Enterprise RAG Platform API")

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(session.router)
