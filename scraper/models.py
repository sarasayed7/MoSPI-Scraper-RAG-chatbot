# Data models (dataclasses or pydantic models) for scraped content
# scraper/models.py

import datetime
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FileLink:
    """Represents a link to a downloadable file."""
    url: str
    file_type: Optional[str] = None # e.g., "pdf", "docx", "xlsx"
    file_path: Optional[str] = None # Local path where the file is saved

@dataclass
class Document:
    """Represents a scraped document/publication."""
    id: str # Unique identifier (e.g., hash of URL or internal ID)
    title: str
    url: str
    date_published: Optional[datetime.date] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    file_links: List[FileLink] = field(default_factory=list)
    content_hash: Optional[str] = None # SHA256 of fetched content for incremental updates
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Table:
    """Represents a table extracted from a PDF."""
    id: str # Unique identifier for the table
    document_id: str # Link to the parent document
    source_file_id: str # Link to the file it was extracted from
    table_json: dict # JSON representation of the table data
    n_rows: int
    n_cols: int
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

# Placeholder for parsed PDF content - will be part of Document initially or a separate entity
@dataclass
class ParsedPdfContent:
    """Represents text extracted from a PDF, potentially chunked."""
    id: str
    document_id: str
    file_path: str
    page_number: int
    text_content: str
    # Consider adding a hash of the text_content for changes in PDF text
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)