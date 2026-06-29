import os

from sqlalchemy.orm import Session

def save_document(db: Session, document):
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, document_model):
    return db.query(document_model).order_by(document_model.created_at.desc()).all()


def delete_document(db: Session, document_model, document_id: str):
    document = db.query(document_model).filter(document_model.id == document_id).first()

    if not document:
        return None

    db.delete(document)
    db.commit()

    return document
