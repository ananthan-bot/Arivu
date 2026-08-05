"""Unit tests for the hybrid retrieval RRF score merging logic."""
from uuid import uuid4

from app.modules.retrieval.services.hybrid_retrieval import HybridRetrievalService, RRF_K
from app.modules.retrieval.repositories.chunk_repository import ChunkRecord


def _make_chunk(text: str) -> ChunkRecord:
    return ChunkRecord(
        id=uuid4(), document_id=uuid4(), filename="doc.md",
        text=text, page=1, heading="Section", chunk_index=0,
    )


class FakeRepo:
    def __init__(self, chunks):
        self._chunks = chunks

    def vector_search(self, query_embedding, top_k):
        return [(c, 0.1 * i) for i, c in enumerate(self._chunks[:top_k])]

    def get_all_ready_chunks(self):
        return self._chunks


class FakeEmbedder:
    def embed_query(self, q):
        return [0.0] * 384


def test_rrf_score_is_higher_for_chunk_ranking_well_in_both_lists():
    c1 = _make_chunk("retrieval augmented generation platform")
    c2 = _make_chunk("the weather is sunny today nothing relevant")
    svc = HybridRetrievalService(FakeRepo([c1, c2]), FakeEmbedder())
    results = svc.retrieve("retrieval platform", top_k=2)
    # c1 should rank higher since it appears in vector results AND matches BM25
    assert results[0][0].text == c1.text


def test_retrieve_returns_at_most_top_k():
    chunks = [_make_chunk(f"chunk number {i}") for i in range(20)]
    svc = HybridRetrievalService(FakeRepo(chunks), FakeEmbedder())
    results = svc.retrieve("chunk", top_k=3)
    assert len(results) <= 3


def test_empty_corpus_returns_empty():
    svc = HybridRetrievalService(FakeRepo([]), FakeEmbedder())
    results = svc.retrieve("anything", top_k=5)
    assert results == []
