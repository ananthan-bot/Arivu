"""HTTP routes for document ingestion. No business logic lives here."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.ingestion.repositories.document_repository import DocumentRepository
from app.modules.ingestion.schemas.document import DocumentResponse
from app.modules.ingestion.services.ingestion_service import IngestionService

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    content = await file.read()
    repo = DocumentRepository(db)
    service = IngestionService(repo)

    try:
        document_id = service.ingest(filename=file.filename, content=content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    document = repo.get_document(document_id)
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        source_type=document.source_type,
        status=document.status,
        created_at=document.created_at,
        chunk_count=len(document.chunks),
    )


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    documents = repo.list_documents()
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            source_type=d.source_type,
            status=d.status,
            created_at=d.created_at,
            chunk_count=len(d.chunks),
        )
        for d in documents
    ]
