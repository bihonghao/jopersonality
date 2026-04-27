"""Utilities for parsing resume files into plain text."""

from __future__ import annotations

from io import BytesIO
from typing import Callable

import fitz  # PyMuPDF
from docx import Document


class ResumeParsingError(Exception):
    """Raised when a resume cannot be parsed into text."""


SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}


def _extract_pdf_text(content: bytes) -> str:
    text_chunks: list[str] = []
    try:
        with fitz.open(stream=content, filetype="pdf") as pdf_document:
            for page in pdf_document:
                text_chunks.append(page.get_text("text"))
    except Exception as exc:  # pylint: disable=broad-except
        raise ResumeParsingError("Failed to parse PDF file.") from exc
    return "\n".join(text_chunks).strip()


def _extract_docx_text(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
    except Exception as exc:  # pylint: disable=broad-except
        raise ResumeParsingError("Failed to parse DOCX file.") from exc

    text_chunks = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
    return "\n".join(text_chunks).strip()


def _extract_txt_text(content: bytes) -> str:
    try:
        return content.decode("utf-8").strip()
    except UnicodeDecodeError:
        try:
            return content.decode("latin-1").strip()
        except Exception as exc:  # pylint: disable=broad-except
            raise ResumeParsingError("Failed to decode TXT file.") from exc


def parse_resume_file(filename: str, content: bytes) -> str:
    """Parse an uploaded resume file and return extracted text."""

    if not filename or "." not in filename:
        raise ResumeParsingError("Unsupported file type. Allowed: pdf, docx, txt.")

    extension = filename.rsplit(".", maxsplit=1)[-1].lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ResumeParsingError("Unsupported file type. Allowed: pdf, docx, txt.")

    if not content:
        raise ResumeParsingError("Uploaded file is empty.")

    extractor_map: dict[str, Callable[[bytes], str]] = {
        "pdf": _extract_pdf_text,
        "docx": _extract_docx_text,
        "txt": _extract_txt_text,
    }

    extracted_text = extractor_map[extension](content)
    if not extracted_text:
        raise ResumeParsingError("No readable text could be extracted from the file.")

    return extracted_text
