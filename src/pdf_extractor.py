"""
PDF Text Extractor Module using PyMuPDF (fitz).

Extracts textual content from in-memory PDF data (bytes or file-like streams)
without persisting files to disk.
"""

from typing import Union, BinaryIO
import io
import pymupdf


class PDFExtractionError(Exception):
    """Base exception for PDF extraction failures."""
    pass


class CorruptedPDFError(PDFExtractionError):
    """Raised when PDF data cannot be opened or parsed."""
    pass


class NoExtractableTextError(PDFExtractionError):
    """Raised when the PDF has no pages or contains no extractable text (e.g., scanned/image-only)."""
    pass


def extract_text_from_pdf(pdf_source: Union[bytes, BinaryIO, io.BytesIO]) -> str:
    """
    Extract text from a PDF provided as raw bytes or a binary file-like stream.

    Args:
        pdf_source: PDF document as bytes, io.BytesIO, or binary stream.

    Returns:
        str: Cleanly extracted text concatenated across all pages.

    Raises:
        ValueError: If input is None, empty, or zero bytes.
        TypeError: If input is not bytes or a file-like stream.
        CorruptedPDFError: If the PDF stream is invalid or malformed.
        NoExtractableTextError: If the PDF has no pages or contains no extractable text.
    """
    if pdf_source is None:
        raise ValueError("PDF source cannot be None.")

    # Read bytes from file-like stream or direct bytes
    if hasattr(pdf_source, "read"):
        if hasattr(pdf_source, "seek"):
            pdf_source.seek(0)
        pdf_bytes = pdf_source.read()
    elif isinstance(pdf_source, (bytes, bytearray)):
        pdf_bytes = bytes(pdf_source)
    else:
        raise TypeError(
            f"Unsupported PDF input type: {type(pdf_source).__name__}. "
            "Expected bytes or binary file-like object."
        )

    if not pdf_bytes:
        raise ValueError("PDF input stream is empty.")

    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise CorruptedPDFError(f"Failed to open PDF document: {exc}") from exc

    try:
        if len(doc) == 0:
            raise NoExtractableTextError("PDF document contains 0 pages.")

        page_texts = []
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text("text")
            if page_text and page_text.strip():
                page_texts.append(page_text.strip())

        if not page_texts:
            raise NoExtractableTextError(
                "PDF contains no extractable text. The file might be blank, "
                "scanned as an image, or require OCR."
            )

        return "\n\n".join(page_texts)
    finally:
        doc.close()
