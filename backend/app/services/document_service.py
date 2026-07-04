from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.config import ALLOWED_EXTENSIONS, CHUNK_OVERLAP, CHUNK_SIZE, CHUNK_STRATEGY
from app.models import Document, DocumentChunk
from app.repositories.chunk_repository import list_chunks as list_chunks_repository
from app.repositories.chunk_repository import save_document_chunks, update_chunk_search_vectors
from app.repositories.document_repository import delete_document as delete_document_repository
from app.repositories.document_repository import list_documents as list_documents_repository
from app.repositories.document_repository import save_document
from app.services.chunking_service import fixed_chunk, paragraph_aware_chunk
from app.services.embedding_service import generate_embedding
from app.utils.file_store import save_uploaded_file


def validate_file_extension(file: UploadFile) -> None:
    """
    Validate that the uploaded file has a supported extension.

    Raises:
        HTTPException: If the file extension is not supported.
    """

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. "
                   f"Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

def extract_text_from_file(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    if extension in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8")

    if extension == ".pdf":
        reader = PdfReader(str(file_path))
        pages_text = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)

        return "\n\n".join(pages_text)

    raise HTTPException(status_code=400, detail="Unsupported file type")

def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    strategy: str = CHUNK_STRATEGY,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be greater than or equal to 0 and less than chunk_size"
        )

    if strategy == "fixed":
        return fixed_chunk(text, chunk_size, overlap)

    if strategy == "paragraph_aware":
        return paragraph_aware_chunk(text, chunk_size, overlap)

    raise ValueError(f"Unsupported chunking strategy: {strategy}")


def upload_document(file: UploadFile, uploaded_by: str, db: Session):
    validate_file_extension(file)

    file_path = save_uploaded_file(file)

    extracted_text = extract_text_from_file(file_path)

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the uploaded document",
        )

    saved_document = save_document(
        db,
        Document(
            filename=Path(file.filename).name,
            source_type="upload",
            uploaded_by=uploaded_by
        )
    )

    text_chunks = chunk_text(extracted_text)

    chunk_records = []

    for index, chunk in enumerate(text_chunks):
        embedding = generate_embedding(chunk)

        chunk_record = DocumentChunk(
            document_id=saved_document.id,
            chunk_text=chunk,
            chunk_index=index,
            embedding=embedding,
            chunk_metadata={
                "filename": saved_document.filename,
                "source_type": saved_document.source_type,
                "chunk_strategy": CHUNK_STRATEGY,
                "chunk_size": CHUNK_SIZE,
                "overlap": CHUNK_OVERLAP,
            },
        )

        chunk_records.append(chunk_record)

    saved_chunks = save_document_chunks(db, chunk_records)

    update_chunk_search_vectors(db)

    return {
        "message": "Document uploaded successfully",
        "document": {
            "id": str(saved_document.id),
            "filename": saved_document.filename,
            "source_type": saved_document.source_type,
            "uploaded_by": saved_document.uploaded_by,
            "created_at": str(saved_document.created_at)
        },
        "chunks_created": len(saved_chunks),
    }


def list_documents(db: Session):
    documents = list_documents_repository(db, Document)

    return [
        {
            "id": str(document.id),
            "filename": document.filename,
            "source_type": document.source_type,
            "uploaded_by": document.uploaded_by,
            "created_at": str(document.created_at)
        }
        for document in documents
    ]


def list_chunks(db: Session):
    chunks = list_chunks_repository(db, Document, DocumentChunk)

    return [
        {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "filename": filename,
            "chunk_index": chunk.chunk_index,
            "chunk_text": chunk.chunk_text,
            "chunk_metadata": chunk.chunk_metadata,
            "created_at": str(chunk.created_at)
        }
        for chunk, filename in chunks
    ]


def delete_document(document_id: str, db: Session):
    try:
        document_uuid = UUID(document_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document id")

    document = delete_document_repository(db, Document, document_uuid)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }
