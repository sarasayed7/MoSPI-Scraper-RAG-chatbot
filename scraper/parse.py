# Logic for downloading and parsing PDFs/other files

# scraper/parse.py

import os
import pdfplumber
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

def parse_pdf(file_path: str) -> Optional[Dict]:
    """
    Parses a PDF file to extract text content and one tabular structure.

    Args:
        file_path (str): The local path to the PDF file.

    Returns:
        Optional[Dict]: A dictionary containing the extracted content or None if parsing fails.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found at: {file_path}")
        return None

    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = ""
            tables_data = []

            # Extract text from all pages
            for page in pdf.pages:
                text_content += page.extract_text() or ""
            
            # Extract tables from the first page (or more if needed)
            first_page = pdf.pages[0]
            tables = first_page.extract_tables()
            if tables:
                logger.info(f"Found {len(tables)} tables on the first page.")
                for table in tables:
                    tables_data.append(table)
            
            return {
                "text": text_content,
                "tables": tables_data
            }
            
    except Exception as e:
        logger.error(f"Error parsing PDF at {file_path}: {e}")
        return None