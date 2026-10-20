"""
Unit tests for PDF extraction module.
Generates in-memory synthetic PDFs using PyMuPDF to test extraction
without requiring external PDF files or fixtures on disk.
"""

import io
import pymupdf
import pytest
from src.pdf_extractor import (
    extract_text_from_pdf,
    CorruptedPDFError,
    NoExtractableTextError,
)


def create_in_memory_pdf(pages_text: list[str]) -> bytes:
    """Helper to generate a minimal valid PDF in memory with specified pages."""
    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page()
        if text.strip():
            page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class TestPDFExtraction:
    """Tests for PDF text extraction from bytes and file-like objects."""

    def test_extract_text_from_bytes(self):
        """Verify successful extraction from raw PDF bytes."""
        sample_text = "Jane Doe\nSenior Backend Developer\nSkills: Python, Go, Docker"
        pdf_bytes = create_in_memory_pdf([sample_text])

        extracted = extract_text_from_pdf(pdf_bytes)
        assert "Jane Doe" in extracted
        assert "Senior Backend Developer" in extracted
        assert "Python, Go, Docker" in extracted

    def test_extract_text_from_file_like_object(self):
        """Verify extraction from io.BytesIO stream."""
        sample_text = "Candidate: Alice Smith\nSpecialization: Machine Learning"
        pdf_bytes = create_in_memory_pdf([sample_text])
        stream = io.BytesIO(pdf_bytes)

        extracted = extract_text_from_pdf(stream)
        assert "Candidate: Alice Smith" in extracted
        assert "Machine Learning" in extracted

    def test_extract_multi_page_pdf(self):
        """Verify all pages of a multi-page PDF are extracted and separated."""
        page1 = "Page 1: Work Experience at Acme Corp"
        page2 = "Page 2: Education and Certifications"
        pdf_bytes = create_in_memory_pdf([page1, page2])

        extracted = extract_text_from_pdf(pdf_bytes)
        assert "Page 1: Work Experience at Acme Corp" in extracted
        assert "Page 2: Education and Certifications" in extracted

    def test_detect_blank_pdf_no_extractable_text(self):
        """Verify that a blank PDF triggers NoExtractableTextError."""
        pdf_bytes = create_in_memory_pdf(["   "])  # Empty page
        with pytest.raises(NoExtractableTextError, match="contains no extractable text"):
            extract_text_from_pdf(pdf_bytes)

    def test_corrupted_pdf_handling(self):
        """Verify that invalid/corrupted bytes raise CorruptedPDFError."""
        corrupted_bytes = b"%PDF-corrupted-stream-data-here"
        with pytest.raises(CorruptedPDFError):
            extract_text_from_pdf(corrupted_bytes)

    def test_empty_input_handling(self):
        """Verify None or empty byte streams raise ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            extract_text_from_pdf(None)

        with pytest.raises(ValueError, match="empty"):
            extract_text_from_pdf(b"")

        with pytest.raises(ValueError, match="empty"):
            extract_text_from_pdf(io.BytesIO(b""))

    def test_unsupported_input_type(self):
        """Verify passing incompatible types raises TypeError."""
        with pytest.raises(TypeError, match="Unsupported PDF input type"):
            extract_text_from_pdf(12345)
