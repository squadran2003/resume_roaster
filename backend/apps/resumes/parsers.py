import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file) -> str:
    """
    Extract plain text from a PDF file object using pypdf.
    Returns empty string on failure (text extraction is best-effort).
    """
    try:
        from pypdf import PdfReader

        file.seek(0)
        reader = PdfReader(io.BytesIO(file.read()))
        parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts)
    except Exception:
        logger.exception("PDF text extraction failed")
        return ""


def extract_text_from_docx(file) -> str:
    """
    Extract plain text from a DOCX file object using python-docx.
    Returns empty string on failure.
    """
    try:
        from docx import Document

        file.seek(0)
        doc = Document(io.BytesIO(file.read()))
        return "\n".join(para.text for para in doc.paragraphs if para.text)
    except Exception:
        logger.exception("DOCX text extraction failed")
        return ""


def extract_text(file, mime_type: str) -> str:
    """Dispatch to the appropriate extractor based on MIME type."""
    if mime_type == "application/pdf":
        return extract_text_from_pdf(file)
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    return ""
