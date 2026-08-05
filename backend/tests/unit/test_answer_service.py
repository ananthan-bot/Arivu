"""Unit tests for the hallucination guard in the answer service."""
from unittest.mock import MagicMock

from app.modules.retrieval.services.answer_service import AnswerService, NO_EVIDENCE_MESSAGE
from app.modules.retrieval.services.context_builder import BuiltContext


def _make_service():
    """Builds an AnswerService with all dependencies mocked out."""
    svc = AnswerService.__new__(AnswerService)
    svc.retriever = MagicMock()
    svc.reranker = MagicMock()
    svc.context_builder = MagicMock()
    svc.llm = MagicMock()
    return svc


def test_hallucination_guard_fires_when_confidence_too_low():
    svc = _make_service()
    svc.retriever.retrieve.return_value = [("chunk", 0.5)]
    svc.reranker.rerank.return_value = [("chunk", 0.1)]
    svc.context_builder.build.return_value = BuiltContext(
        context_text="weak context", chunks=[], top_score=0.1
    )

    result = svc.answer("some query")

    assert result.answered is False
    assert result.answer == NO_EVIDENCE_MESSAGE
    assert svc.llm.generate_answer.called is False


def test_llm_is_called_when_confidence_is_high():
    svc = _make_service()
    svc.retriever.retrieve.return_value = [("chunk", 0.9)]
    svc.reranker.rerank.return_value = [("chunk", 0.9)]
    svc.context_builder.build.return_value = BuiltContext(
        context_text="strong context", chunks=[], top_score=0.9
    )
    svc.llm.generate_answer.return_value = "Arivu is a RAG platform [1]."

    result = svc.answer("what is arivu")

    assert result.answered is True
    assert "Arivu" in result.answer
    assert svc.llm.generate_answer.called is True


def test_no_candidates_returns_no_evidence():
    svc = _make_service()
    svc.retriever.retrieve.return_value = []

    result = svc.answer("anything")

    assert result.answered is False
    assert result.answer == NO_EVIDENCE_MESSAGE
