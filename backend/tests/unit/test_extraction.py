"""Unit tests for the extraction service."""
import pytest

from app.modules.ingestion.services.extraction import ExtractionService


def test_txt_extraction_returns_single_page():
    service = ExtractionService()
    source_type, pages = service.extract("notes.txt", b"Hello, this is a note.")

    assert source_type == "txt"
    assert len(pages) == 1
    assert pages[0].page_number is None
    assert "Hello" in pages[0].text


def test_md_extraction_returns_single_page():
    service = ExtractionService()
    source_type, pages = service.extract("readme.md", b"# Title\nBody text.")

    assert source_type == "md"
    assert len(pages) == 1


def test_unsupported_extension_raises():
    service = ExtractionService()
    with pytest.raises(ValueError):
        service.extract("virus.exe", b"binary")
