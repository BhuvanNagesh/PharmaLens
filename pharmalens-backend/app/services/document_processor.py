"""Extract and normalize text from supported regulatory document formats."""

from __future__ import annotations

import io
import logging
import re
import unicodedata

import pdfplumber
from docx import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph
from PyPDF2 import PdfReader

from app.core.config import settings
from app.services.dolphin_parser import DolphinParserError, extract_pdf_text_with_dolphin


logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Indicate that a supported document could not be processed."""


def clean_extracted_text(text: str) -> str:
    """Normalize extracted text while preserving meaningful paragraph breaks."""
    normalized_text = unicodedata.normalize("NFKC", text)
    normalized_text = normalized_text.replace("\x00", "")
    normalized_text = normalized_text.replace("\r\n", "\n").replace("\r", "\n")
    normalized_text = normalized_text.replace("\u00a0", " ")

    normalized_lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in normalized_text.split("\n")
    ]
    compact_text = "\n".join(normalized_lines)
    compact_text = re.sub(r"\n{3,}", "\n\n", compact_text)
    return compact_text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract PDF text with PyPDF2 first and pdfplumber as a fallback."""
    if not file_bytes:
        raise DocumentProcessingError("The uploaded document is empty.")

    primary_text = ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        primary_text = clean_extracted_text(
            "\n".join(page.extract_text() or "" for page in reader.pages)
        )
        if len(primary_text) > 50:
            return primary_text
    except Exception:
        logger.debug("PyPDF2 could not extract usable PDF text.", exc_info=True)

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            fallback_text = clean_extracted_text(
                "\n".join(page.extract_text() or "" for page in pdf.pages)
            )
    except Exception as error:
        logger.debug("pdfplumber could not extract PDF text.", exc_info=True)
        if primary_text:
            return primary_text
        raise DocumentProcessingError(
            "The PDF could not be read. Verify that it is a valid, text-based PDF."
        ) from error

    return fallback_text or primary_text


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract paragraphs and tables from a DOCX document and normalize them."""
    if not file_bytes:
        raise DocumentProcessingError("The uploaded document is empty.")

    try:
        document = DocxDocument(io.BytesIO(file_bytes))
        blocks: list[str] = []
        for child in document.element.body.iterchildren():
            if child.tag.endswith("}p"):
                paragraph = Paragraph(child, document)
                if paragraph.text.strip():
                    blocks.append(paragraph.text)
            elif child.tag.endswith("}tbl"):
                table = Table(child, document)
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    if any(cells):
                        blocks.append(" | ".join(cells))
        raw_text = "\n".join(blocks)
    except Exception as error:
        logger.debug("python-docx could not extract DOCX text.", exc_info=True)
        raise DocumentProcessingError(
            "The DOCX document could not be read. Verify that it is a valid DOCX file."
        ) from error

    return clean_extracted_text(raw_text)


def _extract_pdf_with_provider(file_bytes: bytes, parser_provider: str | None) -> str:
    """Select native or optional Dolphin extraction for a PDF upload."""
    native_text = extract_text_from_pdf(file_bytes)
    provider = (parser_provider or settings.document_parser_provider).strip().lower()
    if provider not in {"native", "auto", "dolphin"}:
        raise DocumentProcessingError(
            "DOCUMENT_PARSER_PROVIDER must be one of: native, auto, or dolphin."
        )
    if provider == "native":
        return native_text

    should_try_dolphin = (
        provider == "dolphin"
        or len(native_text) <= settings.dolphin_native_text_threshold
    )
    if not should_try_dolphin:
        return native_text

    try:
        enhanced_text = extract_pdf_text_with_dolphin(
            file_bytes,
            model_path=settings.dolphin_model_path,
            device=settings.dolphin_device,
            max_pages=settings.dolphin_max_pages,
            max_new_tokens=settings.dolphin_max_new_tokens,
        )
    except DolphinParserError as error:
        logger.warning("Dolphin extraction unavailable; using native PDF extraction: %s", error)
        return native_text
    except Exception:
        logger.exception("Dolphin extraction failed; using native PDF extraction.")
        return native_text
    return clean_extracted_text(enhanced_text) or native_text


def extract_text(
    file_bytes: bytes,
    file_type: str,
    parser_provider: str | None = None,
) -> str:
    """Extract text from a PDF or DOCX using the configured parser provider."""
    if not isinstance(file_type, str):
        raise DocumentProcessingError(
            "Unsupported document type. Only PDF and DOCX files are supported."
        )
    normalized_file_type = file_type.lower().strip().lstrip(".")
    if normalized_file_type == "pdf":
        return _extract_pdf_with_provider(file_bytes, parser_provider)
    if normalized_file_type == "docx":
        return extract_text_from_docx(file_bytes)
    raise DocumentProcessingError(
        "Unsupported document type. Only PDF and DOCX files are supported."
    )
