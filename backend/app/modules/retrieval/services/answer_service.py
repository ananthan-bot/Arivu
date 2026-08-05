"""
Orchestrates the full query pipeline: hybrid retrieve -> rerank -> build
context -> hallucination guard -> generate answer.

The hallucination guard runs *before* the LLM call, not after: if the
reranker's top score is below the confidence threshold, we return "I don't
have enough evidence" immediately and never call the LLM at all. This is
deliberately conservative -- it's cheaper (no wasted LLM call) and safer
(no chance of the model confidently answering from weak, barely-relevant
context) than trying to detect hallucination after the fact.
"""
from app.core.config import get_settings
from app.modules.retrieval.repositories.chunk_repository import ChunkRepository
from app.modules.retrieval.schemas.query import AnswerResponse, CitationSchema
from app.modules.retrieval.services.context_builder import ContextBuilder
from app.modules.retrieval.services.hybrid_retrieval import HybridRetrievalService
from app.modules.retrieval.services.llm_service import LLMService
from app.modules.retrieval.services.reranking import RerankingService
from app.modules.ingestion.services.embedding import EmbeddingService

settings = get_settings()

NO_EVIDENCE_MESSAGE = "I don't have enough evidence in the available documents to answer that confidently."


class AnswerService:
    def __init__(self, repo: ChunkRepository):
        embedder = EmbeddingService()
        self.retriever = HybridRetrievalService(repo, embedder)
        self.reranker = RerankingService()
        self.context_builder = ContextBuilder()
        self.llm = LLMService()

    def answer(self, query: str, top_k: int = 5) -> AnswerResponse:
        candidates = self.retriever.retrieve(query, top_k=settings.top_k_candidates)

        if not candidates:
            return AnswerResponse(answer=NO_EVIDENCE_MESSAGE, citations=[], confidence=0.0, answered=False)

        reranked = self.reranker.rerank(query, candidates, top_k=top_k)
        context = self.context_builder.build(reranked)

        if context.top_score < settings.hallucination_confidence_threshold:
            return AnswerResponse(
                answer=NO_EVIDENCE_MESSAGE,
                citations=[],
                confidence=context.top_score,
                answered=False,
            )

        answer_text = self.llm.generate_answer(query, context.context_text)

        citations = [
            CitationSchema(
                marker=c.marker,
                filename=c.chunk.filename,
                page=c.chunk.page,
                heading=c.chunk.heading,
            )
            for c in context.chunks
        ]

        return AnswerResponse(
            answer=answer_text,
            citations=citations,
            confidence=context.top_score,
            answered=True,
        )
