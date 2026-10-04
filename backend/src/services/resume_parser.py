import io
import re
import unicodedata
from typing import BinaryIO, Union
import docx
from pypdf import PdfReader


def clean_resume_text(text: str) -> str:
    """
    Cleans and normalizes extracted resume text.
    - Normalizes unicode characters.
    - Standardizes bullet points and dashes.
    - Removes non-printable / control characters.
    - Normalizes excessive whitespace and repeated newlines while preserving structure.
    """
    if not text:
        return ""

    # Normalize unicode to NFKC
    text = unicodedata.normalize("NFKC", text)

    # Standardize bullet symbols
    bullet_pattern = r"[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB\u25CF\u25CB\uF0B7\uF0A7\uF06C\u00B7]"
    text = re.sub(bullet_pattern, "\n- ", text)

    # Standardize quotes and dashes
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")

    # Remove non-printable control characters except \n, \t, \r
    text = "".join(ch for ch in text if ch in ("\n", "\t", "\r") or unicodedata.category(ch)[0] != "C")

    # Replace tabs and multiple spaces on a single line with a single space
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if line:
            lines.append(line)

    # Join lines: collapse more than 2 blank lines into 1
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_text_from_pdf(file_input: Union[bytes, BinaryIO, str]) -> str:
    """Extracts raw text from a PDF file byte stream or path."""
    if isinstance(file_input, bytes):
        stream = io.BytesIO(file_input)
    elif isinstance(file_input, str):
        stream = open(file_input, "rb")
    else:
        stream = file_input

    reader = PdfReader(stream)
    extracted_chunks = []
    for page_idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            extracted_chunks.append(page_text)

    raw_text = "\n\n".join(extracted_chunks)
    return clean_resume_text(raw_text)


def extract_text_from_docx(file_input: Union[bytes, BinaryIO, str]) -> str:
    """Extracts raw text from a DOCX file byte stream or path."""
    if isinstance(file_input, bytes):
        stream = io.BytesIO(file_input)
    elif isinstance(file_input, str):
        stream = file_input
    else:
        stream = file_input

    doc = docx.Document(stream)
    full_text = []

    # Extract paragraphs
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text)

    # Extract table contents if present
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                full_text.append(" | ".join(row_text))

    raw_text = "\n".join(full_text)
    return clean_resume_text(raw_text)


def extract_text_from_txt(file_input: Union[bytes, BinaryIO, str]) -> str:
    """Extracts raw text from a TXT or Markdown file byte stream or path."""
    if isinstance(file_input, bytes):
        try:
            raw_text = file_input.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = file_input.decode("latin-1", errors="ignore")
    elif isinstance(file_input, str):
        with open(file_input, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()
    else:
        content = file_input.read()
        if isinstance(content, bytes):
            raw_text = content.decode("utf-8", errors="ignore")
        else:
            raw_text = content

    return clean_resume_text(raw_text)


def parse_and_clean_resume_file(filename: str, content_bytes: bytes) -> str:
    """
    Detects file format by filename extension, extracts text, and cleans it.
    Raises ValueError on unsupported formats or empty extraction.
    """
    lower_name = filename.lower().strip()
    
    if lower_name.endswith(".pdf"):
        extracted = extract_text_from_pdf(content_bytes)
    elif lower_name.endswith((".docx", ".doc")):
        extracted = extract_text_from_docx(content_bytes)
    elif lower_name.endswith((".txt", ".md", ".rtf")):
        extracted = extract_text_from_txt(content_bytes)
    else:
        # Fallback: attempt pdf then docx then txt
        try:
            extracted = extract_text_from_pdf(content_bytes)
        except Exception:
            try:
                extracted = extract_text_from_docx(content_bytes)
            except Exception:
                extracted = extract_text_from_txt(content_bytes)

    if not extracted or len(extracted.strip()) < 15:
        raise ValueError(
            "Could not extract sufficient text from the uploaded resume file. "
            "Please ensure the file is not scanned/empty or upload a text/PDF format."
        )

    return extracted
