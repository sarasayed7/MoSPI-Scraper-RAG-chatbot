# scraper/crawl.py

import os
import json
import httpx
import logging
import datetime
import hashlib
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import Optional, List

from scraper.models import Document, FileLink

# Load environment variables from .env file
load_dotenv()

# --- Logging Setup ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration from Environment Variables ---
SEED_URL = os.getenv("MOSPI_SEED_URL")
MAX_PAGES = int(os.getenv("MOSPI_MAX_PAGES", 5))
RATE_LIMIT_SECONDS = float(os.getenv("MOSPI_RATE_LIMIT_SECONDS", 1))
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; MoSPIScraper/1.0; +https://yourwebsite.com/)")
PDF_DIR = os.path.join("data", "raw", "pdf")

# Define the data directories
DATA_DIR = os.path.join("data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
PDF_DIR = os.path.join(RAW_DIR, "pdf")

# --- Global state for visited URLs and found documents ---
visited_urls = set()
found_documents = []

# --- HTTP Client Configuration ---
http_client = httpx.Client(
    headers={"User-Agent": USER_AGENT},
    timeout=10
)

def get_page_content(url: str) -> Optional[str]:
    """
    Fetches the content of a given URL.
    """
    if url in visited_urls:
        logger.info(f"Skipping already visited URL: {url}")
        return None

    logger.info(f"Fetching URL: {url}")
    try:
        response = http_client.get(url)
        response.raise_for_status()
        visited_urls.add(url)
        import time
        time.sleep(RATE_LIMIT_SECONDS)
        return response.text
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching {url}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Network error fetching {url}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while fetching {url}: {e}")
    return None

def download_file(url: str, output_dir: str) -> Optional[str]:
    """
    Downloads a file from a URL to a specified directory and returns the local path.
    Only downloads if the file does not already exist.
    """
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_name = url.split('/')[-1]
        file_path = os.path.join(output_dir, file_name)

        # --- NEW INCREMENTAL CHECK ---
        if os.path.exists(file_path):
            logger.info(f"File already exists: {file_path}. Skipping download.")
            return file_path

        logger.info(f"Downloading file from {url} to {file_path}...")
        response = http_client.get(url, follow_redirects=True)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Successfully downloaded file.")
        return file_path
    except Exception as e:
        logger.error(f"Failed to download file from {url}: {e}")
        return None

def parse_listing_page(html_content: str, base_url: str) -> List[Document]:
    """
    Parses a listing page to extract metadata and PDF links directly.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    documents = []

    table_container = soup.find('div', class_='view-content')
    if not table_container:
        logger.error("Could not find the main table container with class 'view-content'.")
        return documents
        
    table = table_container.find('table')
    if not table:
        logger.error("Could not find the main table on the listing page.")
        return documents

    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        if len(cols) < 3: 
            continue 

        subject_cell = cols[1]
        date_cell = cols[2]
        
        title_tag = subject_cell.find('a')
        if not title_tag:
            continue
        
        title = title_tag.get_text(strip=True)
        document_url = urljoin(base_url, title_tag.get('href'))

        date_str = date_cell.get_text(strip=True)
        date_published = None
        try:
            date_published = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
        except ValueError:
            logger.warning(f"Could not parse date '{date_str}' for {title}")

        file_links = []
        pdf_tags = row.find_all('a', href=lambda href: (href and href.lower().endswith('.pdf')))
        for pdf_tag in pdf_tags:
            pdf_url = urljoin(base_url, pdf_tag.get('href'))
            file_links.append(FileLink(url=pdf_url, file_type='pdf'))

        document_id = str(hash(document_url))
        new_document = Document(
            id=document_id,
            title=title,
            url=document_url,
            date_published=date_published,
            file_links=file_links,
        )
        documents.append(new_document)

    logger.info(f"Parsed {len(documents)} documents from the listing page.")
    return documents

def crawl_website(seed_url: str, max_pages: int):
    """
    Main function to crawl the website, starting from a seed URL.
    This version processes documents directly from the listing page and handles pagination.
    """
    queue = [seed_url]
    pages_crawled = 0

    while queue and pages_crawled < max_pages:
        current_url = queue.pop(0)

        html_content = get_page_content(current_url)
        if html_content:
            pages_crawled += 1

            if "press-release" in current_url:
                new_documents = parse_listing_page(html_content, current_url)
                found_documents.extend(new_documents)

                soup = BeautifulSoup(html_content, 'html.parser')
                pagination_container = soup.find('ul', class_='pager')
                
                if pagination_container:
                    logger.info("Pagination container found. Checking for next page links.")
                    for li_tag in pagination_container.find_all('li'):
                        page_link_tag = li_tag.find('a')
                        
                        if page_link_tag and page_link_tag.get('href'):
                            pagination_url = urljoin(current_url, page_link_tag.get('href'))
                            
                            if pagination_url not in visited_urls and pagination_url not in queue and pages_crawled < max_pages:
                                logger.info(f"Found new pagination link: {pagination_url}. Adding to queue.")
                                queue.append(pagination_url)
                else:
                    logger.info("No pagination container found on this page.")
            else:
                logger.warning(f"Encountered unexpected page type: {current_url}. Skipping.")
        else:
            logger.warning(f"Failed to get content for: {current_url}")

    logger.info(f"Crawl finished. Found {len(found_documents)} documents.")

    # --- NEW LOGIC: Download all files from the scraped documents and save metadata ---
    logger.info("Starting file download process...")
    files_to_download = []
    for doc in found_documents:
        for file_link in doc.file_links:
            files_to_download.append(file_link.url)
    
    unique_files = list(set(files_to_download))
    logger.info(f"Found {len(unique_files)} unique files to download.")
    
    for file_url in unique_files:
        if file_url.endswith('.pdf'):
            download_file(file_url, PDF_DIR)

    logger.info("File download process finished.")
    
    # --- Save the crawled documents to a JSON file ---
    if found_documents:
        output_path = os.path.join(RAW_DIR, "crawled_documents.json")
        try:
            docs_to_save = [d.to_dict() for d in found_documents]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(docs_to_save, f, indent=4)
            logger.info(f"Successfully saved {len(found_documents)} document records to {output_path}.")
        except Exception as e:
            logger.error(f"Failed to save crawled documents to file: {e}")
    
    return found_documents

if __name__ == "__main__":
    if not SEED_URL:
        logger.error("MOSPI_SEED_URL environment variable not set. Please configure .env.example.")
    else:
        logger.info(f"Starting crawl from {SEED_URL} for {MAX_PAGES} pages.")
        scraped_docs = crawl_website(SEED_URL, MAX_PAGES)
        logger.info(f"Total documents scraped: {len(scraped_docs)}")