

import os
import re
from pathlib import Path
from typing import Optional
import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            full_text.append(f"--- PAGE {i} ---\n{text}")

    return "\n\n".join(full_text)


def extract_tables_from_pdf(pdf_path: str) -> list[list]:

    all_cells = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    clean_row = [cell.strip() if cell else "" for cell in row]
                    all_cells.append(clean_row)
    return all_cells


def get_pdf_metadata(pdf_path: str) -> dict:
    """Return basic metadata about the PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        meta = pdf.metadata or {}
        return {
            "page_count": len(pdf.pages),
            "title": meta.get("Title", ""),
            "author": meta.get("Author", ""),
            "creator": meta.get("Creator", ""),
            "file_name": Path(pdf_path).name,
            "file_size_kb": round(os.path.getsize(pdf_path) / 1024, 1),
        }


def load_fnol_document(pdf_path: str) -> dict:
    
    return {
        "raw_text": extract_text_from_pdf(pdf_path),
        "tables": extract_tables_from_pdf(pdf_path),
        "metadata": get_pdf_metadata(pdf_path),
    }
