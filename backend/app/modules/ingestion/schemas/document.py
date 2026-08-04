"""Request/response schemas for the ingestion module."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    source_type: str
    status: str
    created_at: datetime
    chunk_count: int = 0


class ChunkPreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    page: int | None
    chunk_index: int
    heading: str | None
