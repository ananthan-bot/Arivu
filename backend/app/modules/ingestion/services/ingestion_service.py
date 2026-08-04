"""
Orchestrates the ingestion pipeline: extract -> chunk -> embed -> persist.

This is the composition root for the pipeline. Each stage is its own class
with a single responsibility (extraction, chunking, embedding) so they can
be unit tested independently and swapped without touching this file's
control flow.
"""
import logging
import uuid

from app.modules.ingestion.repositories.document_repository import DocumentRepository
from app.modules.ingestion.services.chunking import ChunkingService
from app.modules.ingestion.services.embedding import EmbeddingService
from app.modules.ingestion.services.extraction import ExtractionService

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo
        self.extractor = ExtractionService()
        self.chunker = ChunkingService()
        self.embedder = EmbeddingService()

    def ingest(self, filename: str, content: bytes) -> uuid.UUID:
        source_type, pages = self.extractor.extract(filename, content)
        document = self.repo.create_document(filename=filename, source_type=source_type)

        try:
            chunks = self.chunker.chunk_pages(pages)
            if not chunks:
                self.repo.mark_status(document.id, "failed")
                raise ValueError("No extractable text found in document.")

            vectors = self.embedder.embed_texts([c.text for c in chunks])

            rows = [
                {
                    "id": uuid.uuid4(),
                    "document_id": document.id,
                    "text": c.text,
                    "page": c.page,
                    "chunk_index": c.chunk_index,
                    "heading": c.heading,
                    "embedding": vector,
                }
                for c, vector in zip(chunks, vectors)
            ]
            self.repo.add_chunks(document.id, rows)
            self.repo.mark_status(document.id, "ready")
            logger.info("Ingested %s: %d chunks", filename, len(rows))
        except Exception:
            self.repo.mark_status(document.id, "failed")
            logger.exception("Ingestion failed for %s", filename)
            raise

        return document.id
