"""Unit tests for heading-aware recursive chunking. No DB or model needed."""
from app.modules.ingestion.services.chunking import ChunkingService
from app.modules.ingestion.services.extraction import ExtractedPage


def test_chunks_respect_headings():
    text = (
        "# Section A\n"
        "Some content in section A.\n\n"
        "# Section B\n"
        "Some different content in section B.\n"
    )
    chunks = ChunkingService().chunk_pages([ExtractedPage(page_number=1, text=text)])

    assert len(chunks) == 2
    assert chunks[0].heading == "Section A"
    assert chunks[1].heading == "Section B"
    assert "section A" in chunks[0].text
    assert "section B" in chunks[1].text


def test_chunks_track_page_numbers():
    pages = [
        ExtractedPage(page_number=1, text="Page one content here."),
        ExtractedPage(page_number=2, text="Page two content here."),
    ]
    chunks = ChunkingService().chunk_pages(pages)

    pages_seen = {c.page for c in chunks}
    assert pages_seen == {1, 2}


def test_long_section_is_split_with_overlap():
    long_paragraph = " ".join([f"sentence number {i} about the topic." for i in range(200)])
    chunks = ChunkingService().chunk_pages([ExtractedPage(page_number=1, text=long_paragraph)])

    assert len(chunks) > 1, "A long section should be split into multiple chunks"


def test_empty_text_produces_no_chunks():
    chunks = ChunkingService().chunk_pages([ExtractedPage(page_number=1, text="   \n\n  ")])
    assert chunks == []
