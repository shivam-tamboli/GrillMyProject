from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PyPdfError


class ResumeError(Exception):
    """The file is not a readable PDF, or it has no text in it."""


def is_pdf(data: bytes) -> bool:
    return data[:5] == b"%PDF-"


def extract_text(data: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(data))
        if reader.is_encrypted:
            raise ResumeError("PDF is password protected")
        pages = [page.extract_text() or "" for page in reader.pages]
    except PyPdfError as e:
        raise ResumeError("could not read PDF") from e

    text = "\n".join(pages).strip()
    if not text:
        raise ResumeError("no text found in PDF, it may be a scanned image")
    return text
