"""Data-access layer for documents and chunks. Services never touch SQLAlchemy directly."""
import uuid

from sqlalchemy.orm import Session

from app.modules.ingestion.models.document import Chunk, Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, filename: str, source_type: str) -> Document:
        doc = Document(filename=filename, source_type=source_type, status="processing")
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def add_chunks(self, document_id: uuid.UUID, chunk_rows: list[dict]) -> None:
        self.db.bulk_insert_mappings(Chunk, chunk_rows)
        self.db.commit()

    def mark_status(self, document_id: uuid.UUID, status: str) -> None:
        doc = self.db.get(Document, document_id)
        if doc:
            doc.status = status
            self.db.commit()

    def list_documents(self) -> list[Document]:
        return self.db.query(Document).order_by(Document.created_at.desc()).all()

    def get_document(self, document_id: uuid.UUID) -> Document | None:
        return self.db.get(Document, document_id)
