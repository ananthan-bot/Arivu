"""HTTP routes for querying the knowledge base. No business logic here."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.retrieval.repositories.chunk_repository import ChunkRepository
from app.modules.retrieval.schemas.query import AnswerResponse, QueryRequest
from app.modules.retrieval.services.answer_service import AnswerService

router = APIRouter(prefix="/api/v1/query", tags=["query"])


@router.post("", response_model=AnswerResponse)
def query(request: QueryRequest, db: Session = Depends(get_db)):
    repo = ChunkRepository(db)
    service = AnswerService(repo)
    return service.answer(request.query, top_k=request.top_k)
