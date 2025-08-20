# Main ETL script to transform raw data
# pipeline/run.py

import os
import json
import logging
import pandas as pd
from typing import List, Dict

# Assumed import of the custom scraper files
from scraper.models import Document
from scraper.parse import parse_pdf 

logger = logging.getLogger(__name__)

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

        # Process each file link associated with the document
        processed_files = []
        for file_link in doc.file_links:
            if file_link.file_type == 'pdf':
                # Assuming the PDF was downloaded and saved with its original filename
                file_name = file_link.url.split('/')[-1]
                file_path = os.path.join(pdf_dir, file_name)
                
                pdf_content = parse_pdf(file_path)
                
                if pdf_content:
                    # Store processed content (text and tables) as a new field
                    processed_files.append({
                        "url": file_link.url,
                        "path": file_path,
                        "text_content": pdf_content.get("text", ""),
                        "tables_json": json.dumps(pdf_content.get("tables", []))
                    })
        
        # Now, create a final structured record for storage
        doc_record = {
            "id": doc.id,
            "title": doc.title,
            "url": doc.url,
            "date_published": str(doc.date_published),
            "processed_files": processed_files
        }
        processed_documents.append(doc_record)

    # --- Store the processed data (e.g., as JSON or a structured file) ---
    output_path = os.path.join(processed_dir, "processed_documents.json")
    with open(output_path, 'w') as f:
        json.dump(processed_documents, f, indent=4)

    logger.info(f"ETL process finished. Processed {len(processed_documents)} documents.")
    logger.info(f"Processed data stored at: {output_path}")

if __name__ == "__main__":
    # This is a placeholder; in a real scenario, this would be integrated with the crawler
    # or orchestrated via a Makefile.
    # For now, you can manually test it with a sample Document list.
    logger.info("This script is designed to be run as part of a larger pipeline.")
    logger.info("Please ensure your PDFs are downloaded in the data/raw/pdf directory.")