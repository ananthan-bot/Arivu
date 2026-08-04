"""Data access for retrieval: vector similarity search + bulk fetch for BM25."""
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ingestion.models.document import Chunk, Document


@dataclass
class ChunkRecord:
    id: UUID
    document_id: UUID
    filename: str
    text: str
    page: int | None
    heading: str | None
    chunk_index: int


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def vector_search(self, query_embedding: list[float], top_k: int) -> list[tuple[ChunkRecord, float]]:
        """
        Returns (chunk, distance) pairs ordered by cosine distance (ascending —
        lower is more similar). Uses pgvector's `<=>` operator, which is index-
        accelerated once an IVFFlat/HNSW index exists on `chunks.embedding`.
        """
        rows = (
            self.db.query(Chunk, Document.filename, Chunk.embedding.cosine_distance(query_embedding).label("distance"))
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.status == "ready")
            .order_by("distance")
            .limit(top_k)
            .all()
        )
        return [
            (
                ChunkRecord(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    filename=filename,
                    text=chunk.text,
                    page=chunk.page,
                    heading=chunk.heading,
                    chunk_index=chunk.chunk_index,
                ),
                distance,
            )
            for chunk, filename, distance in rows
        ]

    def get_all_ready_chunks(self) -> list[ChunkRecord]:
        """
        Fetches every chunk from successfully-ingested documents, for BM25
        indexing. Fine at demo/portfolio scale (hundreds-low thousands of
        chunks); at real enterprise scale this is exactly where you'd swap
        in Elasticsearch's built-in BM25 instead of rebuilding an in-memory
        index per query — a good thing to say out loud in the interview.
        """
        rows = (
            self.db.query(Chunk, Document.filename)
            .join(Document, Chunk.document_id == Document.id)
            .filter(Document.status == "ready")
            .all()
        )
        return [
            ChunkRecord(
                id=chunk.id,
                document_id=chunk.document_id,
                filename=filename,
                text=chunk.text,
                page=chunk.page,
                heading=chunk.heading,
                chunk_index=chunk.chunk_index,
            )
            for chunk, filename in rows
        ]
