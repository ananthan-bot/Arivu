"""
Extracts raw text (with page numbers where applicable) from uploaded files.

Kept deliberately narrow for the 4-day build: PDF, TXT, MD. The interface
(`extract`) is the seam where DOCX/PPTX/OCR would plug in later without
touching chunking or embedding code — that's the point of keeping this as
its own service rather than inlining file parsing into the controller.
"""
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


@dataclass
class ExtractedPage:
    """One page (or the whole doc, for non-paginated formats) of raw text."""
    page_number: int | None
    text: str


class ExtractionService:
    """Routes a file to the right parser based on its extension."""

    SUPPORTED_TYPES = {"pdf", "txt", "md"}

    def extract(self, filename: str, content: bytes) -> tuple[str, list[ExtractedPage]]:
        """
        Returns (source_type, pages). Raises ValueError for unsupported types.
        """
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if ext not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported file type: .{ext}. Supported: {self.SUPPORTED_TYPES}")

        if ext == "pdf":
            return "pdf", self._extract_pdf(content)
        return ext, [ExtractedPage(page_number=None, text=content.decode("utf-8", errors="ignore"))]

    def _extract_pdf(self, content: bytes) -> list[ExtractedPage]:
        reader = PdfReader(BytesIO(content))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(ExtractedPage(page_number=i, text=text))
        return pages
