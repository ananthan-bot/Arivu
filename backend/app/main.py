"""Arivu backend entrypoint."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import Base, engine
from app.modules.ingestion.controllers.document_controller import router as documents_router
# Importing the models module registers Document/Chunk on Base.metadata --
# required before create_all(), even though nothing else references it here.
from app.modules.ingestion.models import document  # noqa: F401

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to the deployed frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)


@app.on_event("startup")
def initialize_database() -> None:
    """
    Creates the pgvector extension and any missing tables on startup.

    This is a pragmatic choice for the current stage of the project -- a
    real production system would use Alembic migrations (already in
    requirements.txt) so schema changes are versioned and reviewable
    instead of implicitly applied on boot. Worth calling out as a known
    simplification if asked in an interview.
    """
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema verified/created on startup.")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "environment": settings.environment}
