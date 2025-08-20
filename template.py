# template.py

import os
from pathlib import Path

def create_project_skeleton():
    """
    Creates the directory and file structure for the MoSPI Scraper & RAG Chatbot project.
    """
    project_root = Path('.')

    # Define the core directories from the assignment's skeleton
    dirs = [
        'scraper',
        'scraper/tests',
        'pipeline',
        'pipeline/tests',
        'rag',
        'rag/tests',
        'ui',
        'ui/tests',
        'data/raw',
        'data/processed',
        'infra'
    ]

    # Create directories
    print("Creating project directories...")
    for dir_name in dirs:
        os.makedirs(project_root / dir_name, exist_ok=True)
        print(f"  - Created {dir_name}/")

    # Define core files and their initial content (using placeholder comments)
    files = {
        'README.md': "# MoSPI Scraper + LLaMA RAG Chatbot\n\nThis project builds a web scraper for the Ministry of Statistics and Programme Implementation (MoSPI) and a RAG chatbot using a local LLaMA model.\n\n## Setup\n\n## Running\n\n## Architecture & Trade-offs\n\n",
        'Makefile': """
# Makefile for orchestrating the project components

.PHONY: crawl etl index up

crawl:
\t@echo "Running web scraper..."
\tpython -m scraper.crawl

etl:
\t@echo "Running ETL pipeline..."
\tpython -m pipeline.run

index: etl
\t@echo "Building RAG vector index..."
\tpython -m rag.retriever.index

up:
\t@echo "Bringing up all services with Docker Compose..."
\tdocker compose up

clean:
\t@echo "Cleaning data artifacts..."
\trm -rf data/raw/* data/processed/*
\t@echo "Cleaning up Docker containers..."
\tdocker compose down -v --remove-orphans
""",
        'docker-compose.yml': """
# docker-compose.yml for the project services

services:
  scraper:
    build:
      context: .
      dockerfile: ./infra/Dockerfile.scraper
    container_name: mospi-scraper
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    networks:
      - rag-network
    command: python -m scraper.crawl

  api:
    build:
      context: .
      dockerfile: ./infra/Dockerfile.api
    container_name: rag-api
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    depends_on:
      - scraper # Ensure scraper is done first (for initial data)
      - ollama
    networks:
      - rag-network
    command: uvicorn rag.api:app --host 0.0.0.0 --port 8000

  ui:
    build:
      context: .
      dockerfile: ./infra/Dockerfile.ui
    container_name: rag-ui
    env_file:
      - .env
    ports:
      - "3000:3000" # Example for a Next.js/React app
    depends_on:
      - api
    networks:
      - rag-network

  ollama:
    container_name: ollama
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - rag-network

volumes:
  ollama-data:

networks:
  rag-network:
    driver: bridge
""",
        '.env.example': """
# [cite_start].env.example with all configurable settings [cite: 12]

# Scraper configuration
MOSPI_SEED_URL="https://www.mospi.gov.in/web/mospi/press-note"
MOSPI_MAX_PAGES=5
MOSPI_RATE_LIMIT_SECONDS=1
USER_AGENT="Mozilla/5.0 (compatible; MoSPIScraper/1.0; +https://yourwebsite.com/)"

# ETL configuration
CHUNK_SIZE=1024
CHUNK_OVERLAP=200

# RAG configuration
OLLAMA_MODEL="llama3"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
VECTOR_STORE_PATH="./data/processed/vector_store"
TOP_K=5
TEMPERATURE=0.0
""",
        # Scraper files
        'scraper/__init__.py': "",
        'scraper/crawl.py': "# Main scraper logic for crawling and parsing listing pages",
        'scraper/parse.py': "# Logic for downloading and parsing PDFs/other files",
        'scraper/models.py': "# Data models (dataclasses or pydantic models) for scraped content",
        # Pipeline files
        'pipeline/__init__.py': "",
        'pipeline/run.py': "# Main ETL script to transform raw data",
        'pipeline/validate.py': "# Data validation and quality checks",
        # RAG files
        'rag/__init__.py': "",
        'rag/api.py': "# FastAPI/Flask API endpoints for the chatbot [cite: 82]",
        'rag/retriever.py': "# Retrieval logic (embedding, vector search)",
        'rag/prompt.py': "# Prompt engineering logic for the LLM",
        # Infra files
        'infra/Dockerfile.scraper': """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scraper/ /app/scraper
COPY data/ /app/data
CMD ["python", "-m", "scraper.crawl"]
""",
        'infra/Dockerfile.api': """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rag/ /app/rag
COPY data/ /app/data
EXPOSE 8000
CMD ["uvicorn", "rag.api:app", "--host", "0.0.0.0", "--port", "8000"]
""",
        'infra/Dockerfile.ui': """
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
""",
    }

    # Write files
    print("\nCreating project files...")
    for file_name, content in files.items():
        file_path = project_root / file_name
        # Skip creating Dockerfile.ui if the user prefers a Python UI (e.g., Streamlit)
        if 'Dockerfile.ui' in file_name and 'Streamlit' in content:
            continue
        if not file_path.exists() or 'Dockerfile' in file_name: # Overwrite Dockerfiles to ensure they are correct
            with open(file_path, 'w') as f:
                f.write(content.strip())
            print(f"  - Created {file_name}")

if __name__ == '__main__':
    create_project_skeleton()
    print("\nProject skeleton created successfully! 🥳")
    print("Next steps:")
    print("1. Navigate to the project root directory.")
    print("2. Create a virtual environment: `python -m venv venv`")
    print("3. Activate it: `source venv/bin/activate`")
    print("4. Install dependencies (create a requirements.txt file first).")
    print("5. Run `python template.py` again to check for missing files.")
    print("6. Begin implementing the logic in each file. Good luck! 😊")