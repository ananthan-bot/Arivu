"""Unit tests for the context builder service."""
from uuid import uuid4

from app.modules.retrieval.repositories.chunk_repository import ChunkRecord
from app.modules.retrieval.services.context_builder import ContextBuilder


def _make_chunk(text: str, heading: str = "Section", page: int = 1) -> ChunkRecord:
    return ChunkRecord(
        id=uuid4(),
        document_id=uuid4(),
        filename="doc.md",
        text=text,
        page=page,
        heading=heading,
        chunk_index=0,
    )


def test_citation_markers_are_sequential():
    c1 = _make_chunk("Arivu is a RAG platform.")
    c2 = _make_chunk("It uses hybrid retrieval.")
    result = ContextBuilder().build([(c1, 0.9), (c2, 0.8)])
    assert result.chunks[0].marker == "[1]"
    assert result.chunks[1].marker == "[2]"


def test_near_duplicate_is_removed():
    c1 = _make_chunk("Arivu uses hybrid retrieval combining vector search and BM25 keyword search.")
    c2 = _make_chunk("Arivu uses hybrid retrieval combining vector search and BM25 keyword matching.")
    result = ContextBuilder().build([(c1, 0.9), (c2, 0.85)])
    assert len(result.chunks) == 1


def test_top_score_is_highest_reranker_score():
    c1 = _make_chunk("First chunk.")
    c2 = _make_chunk("Second chunk.")
    result = ContextBuilder().build([(c1, 0.9), (c2, 0.5)])
    assert result.top_score == 0.9


def test_empty_candidates_returns_empty_context():
    result = ContextBuilder().build([])
    assert result.context_text == ""
    assert result.chunks == []
    assert result.top_score == 0.0


def test_context_includes_filename_and_heading():
    chunk = _make_chunk("Some content.", heading="Introduction", page=2)
    result = ContextBuilder().build([(chunk, 0.9)])
    assert "doc.md" in result.context_text
    assert "Introduction" in result.context_text
    assert "page 2" in result.context_text
