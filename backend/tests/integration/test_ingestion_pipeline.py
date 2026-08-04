"""
Integration test: extraction -> chunking -> embedding -> persistence.

Requires a real Postgres with pgvector reachable at DATABASE_URL (see
tests/conftest.py's test_db fixture and .env.example for local setup).
"""
from app.modules.ingestion.repositories.document_repository import DocumentRepository
from app.modules.ingestion.services.ingestion_service import IngestionService


def test_ingest_persists_document_and_chunks(test_db):
    repo = DocumentRepository(test_db)
    service = IngestionService(repo)

    content = b"# Intro\nThis document is about testing the ingestion pipeline end to end."
    document_id = service.ingest(filename="test.md", content=content)

    document = repo.get_document(document_id)
    assert document is not None
    assert document.status == "ready"
    assert len(document.chunks) >= 1
    assert document.chunks[0].heading == "Intro"
    assert len(document.chunks[0].embedding) == 384
