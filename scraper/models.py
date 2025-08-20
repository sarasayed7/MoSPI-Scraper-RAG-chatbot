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

    def to_dict(self):
        """Converts the FileLink object to a dictionary."""
        return {
            "url": self.url,
            "file_type": self.file_type,
            "file_path": self.file_path,
        }

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

    def to_dict(self):
        """Converts the Document object to a dictionary for JSON serialization."""
        doc_dict = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            # Convert date objects to ISO 8601 string format
            "date_published": self.date_published.isoformat() if self.date_published else None,
            "category": self.category,
            "summary": self.summary,
            "content_hash": self.content_hash,
            # Convert nested FileLink objects
            "file_links": [link.to_dict() for link in self.file_links],
            "created_at": self.created_at.isoformat(),
        }
        return doc_dict

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

    def to_dict(self):
        """Converts the Table object to a dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "source_file_id": self.source_file_id,
            "table_json": self.table_json,
            "n_rows": self.n_rows,
            "n_cols": self.n_cols,
            "created_at": self.created_at.isoformat(),
        }

# Placeholder for parsed PDF content - will be part of Document initially or a separate entity
@dataclass
class ParsedPdfContent:
    """Represents text extracted from a PDF, potentially chunked."""
    id: str
    document_id: str
    file_path: str
    page_number: int
    text_content: str
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_dict(self):
        """Converts the ParsedPdfContent object to a dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "file_path": self.file_path,
            "page_number": self.page_number,
            "text_content": self.text_content,
            "created_at": self.created_at.isoformat(),
        }