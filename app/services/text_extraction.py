import pdfplumber
import docx2txt
from pathlib import Path
from fastapi import HTTPException, status


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error extracting text from PDF: {str(e)}"
        )
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from DOCX file."""
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error extracting text from DOCX: {str(e)}"
        )


def extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats."""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".txt":
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file_ext}"
        )