"""Request/response schemas for the query/answer endpoint."""
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class CitationSchema(BaseModel):
    marker: str
    filename: str
    page: int | None
    heading: str | None


class AnswerResponse(BaseModel):
    answer: str
    citations: list[CitationSchema]
    confidence: float
    answered: bool  # False when the hallucination guard declined to answer
