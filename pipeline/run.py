# Main ETL script to transform raw data
# pipeline/run.py

import os
import json
import logging
from typing import List, Dict
import datetime

# Assumed import of the custom scraper files
from scraper.models import Document, FileLink
from scraper.parse import parse_pdf 

logger = logging.getLogger(__name__)

# Define the data directories
DATA_DIR = os.path.join("data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
PDF_DIR = os.path.join(RAW_DIR, "pdf")

def validate_document(doc: Document) -> bool:
    """
    Performs basic data quality checks on a document.
    """
    if not doc.title or not doc.url:
        logger.warning(f"Invalid document due to missing title or URL: {doc.id}")
        return False
    # Additional validation checks can go here
    return True

def process_scraped_data(crawled_docs: List[Document], pdf_dir: str, processed_dir: str):
    """
    Orchestrates the ETL process: reads scraped data, parses PDFs, and stores processed data.
    """
    logger.info("Starting ETL process...")
    processed_documents = []

    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)

    for doc in crawled_docs:
        if not validate_document(doc):
            continue

        processed_files = []
        for file_link in doc.file_links:
            if file_link.file_type == 'pdf':
                file_name = file_link.url.split('/')[-1]
                file_path = os.path.join(pdf_dir, file_name)
                
                pdf_content = parse_pdf(file_path)
                
                if pdf_content:
                    processed_files.append({
                        "url": file_link.url,
                        "path": file_path,
                        "text_content": pdf_content.get("text", ""),
                        "tables_json": json.dumps(pdf_content.get("tables", []))
                    })
        
        doc_record = {
            "id": doc.id,
            "title": doc.title,
            "url": doc.url,
            "date_published": doc.date_published,
            "processed_files": processed_files
        }
        processed_documents.append(doc_record)

    output_path = os.path.join(processed_dir, "processed_documents.json")
    with open(output_path, 'w') as f:
        # Use a custom function to handle non-serializable objects
        json.dump(processed_documents, f, indent=4, default=str)

    logger.info(f"ETL process finished. Processed {len(processed_documents)} documents.")
    logger.info(f"Processed data stored at: {output_path}")

if __name__ == "__main__":
    # This block will now load the data and call the processing function
    crawled_docs_path = os.path.join(RAW_DIR, "crawled_documents.json")
    
    if not os.path.exists(crawled_docs_path):
        logger.error(f"Crawled documents file not found at: {crawled_docs_path}")
        logger.error("Please run the scraper.crawl script first to generate this file.")
    else:
        with open(crawled_docs_path, 'r') as f:
            raw_docs_data = json.load(f)
            
        # Manually reconstruct Document objects from the dictionary data
        crawled_docs = []
        for d in raw_docs_data:
            doc = Document(
                id=d['id'],
                title=d['title'],
                url=d['url'],
                date_published=datetime.datetime.fromisoformat(d['date_published']).date() if d['date_published'] else None,
                file_links=[FileLink(**link) for link in d['file_links']]
            )
            crawled_docs.append(doc)

        process_scraped_data(crawled_docs, PDF_DIR, PROCESSED_DIR)