"""Unit tests for the reranking service."""
from unittest.mock import patch
from uuid import uuid4

from app.modules.retrieval.repositories.chunk_repository import ChunkRecord
from app.modules.retrieval.services.reranking import RerankingService


def _make_chunk(text: str) -> ChunkRecord:
    return ChunkRecord(
        id=uuid4(), document_id=uuid4(), filename="doc.md",
        text=text, page=1, heading="Section", chunk_index=0,
    )


def test_reranking_orders_by_score_descending():
    c1 = _make_chunk("about retrieval systems")
    c2 = _make_chunk("about the weather today")

    with patch("app.modules.retrieval.services.reranking._get_cross_encoder") as mock_get:
        mock_model = mock_get.return_value
        mock_model.predict.return_value = [0.9, 0.1]

        svc = RerankingService()
        results = svc.rerank("retrieval", [(c1, 0.5), (c2, 0.5)], top_k=2)

    assert results[0][0].text == c1.text
    assert results[0][1] == 0.9
    assert results[1][1] == 0.1


def test_reranking_returns_top_k_only():
    chunks = [(_make_chunk(f"chunk {i}"), 0.5) for i in range(10)]

    with patch("app.modules.retrieval.services.reranking._get_cross_encoder") as mock_get:
        mock_model = mock_get.return_value
        mock_model.predict.return_value = [float(i) for i in range(10)]

        svc = RerankingService()
        results = svc.rerank("query", chunks, top_k=3)

    assert len(results) == 3


def test_empty_candidates_returns_empty():
    svc = RerankingService()
    results = svc.rerank("query", [], top_k=5)
    assert results == []
