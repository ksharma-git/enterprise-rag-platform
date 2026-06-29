from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SearchRequest
from app.services.document_service import delete_document as delete_document_service
from app.services.document_service import list_chunks as list_chunks_service
from app.services.document_service import list_documents as list_documents_service
from app.services.document_service import upload_document as upload_document_service
from app.services.retrieval_service import search_documents as search_documents_service

router = APIRouter()


@router.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    uploaded_by: str = "kamal",
    db: Session = Depends(get_db),
):
    return upload_document_service(file, uploaded_by, db)


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    return list_documents_service(db)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    return delete_document_service(document_id, db)


@router.get("/chunks")
def list_chunks(db: Session = Depends(get_db)):
    return list_chunks_service(db)


@router.post("/search")
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    return search_documents_service(request.query, request.top_k, db)
