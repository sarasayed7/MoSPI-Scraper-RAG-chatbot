MoSPI Scraper + LLaMA-powered Q&A Chatbot 🤖
This project builds an end-to-end Retrieval-Augmented Generation (RAG) system. It includes a web scraper for collecting public statistical content from the Ministry of Statistics and Programme Implementation (MoSPI) website, an ETL (Extract, Transform, Load) pipeline to process PDF documents, and a small Q&A chatbot powered by a local LLaMA 3 (or Phi-3) model.

🎯 Deliverables Summary
Code Repository: Organized code (/scraper, /pipeline, /rag, /infra), README.md, .env.example, and tests.

Data Artifacts: Processed data (Parquet/CSV), and a FAISS vector index.

Runnable Demo: A docker-compose setup to bring up all components (scraper, pipeline, RAG API, web UI) with a single command.

Short Notes: Explanations of architecture, trade-offs, and future improvements (can be part of this README).

(Optional Bonus) Screen-recording Demo: A short video demonstrating the chatbot.

✨ Features
Web Scraper: Collects content and metadata from MoSPI, handling PDF downloads and text/table extraction.

ETL Pipeline: Processes raw data, chunks text, and prepares it for vector indexing.

Vector Indexing: Creates a FAISS index from document chunks for efficient retrieval.

RAG Chatbot API: A FastAPI backend that retrieves relevant context from the FAISS index and uses a local LLaMA 3 (or Phi-3) model (via Ollama) to answer user questions.

Streamlit Frontend: A simple, interactive web UI for the chatbot.

Dockerization: All components are containerized for easy deployment and reproducibility.

🛠️ Tech Stack
Languages: Python 3.11+

Web Scraping: requests, beautifulsoup4, pdfplumber

Data Handling: numpy, pandas

RAG: sentence-transformers, faiss-cpu

LLM Runtime: Ollama (for LLaMA 3 Instruct / Phi-3)

API: FastAPI, uvicorn

UI: Streamlit

Containerization: Docker, docker-compose

🚀 Setup & Running the Project
The recommended way to run this project is using Docker Compose, as it handles all services (Ollama, API, UI, and a pipeline container for running scripts) in isolated environments.

Prerequisites
Git: For cloning the repository.

Docker Desktop: Install Docker Desktop for your operating system (Windows, macOS, Linux). Ensure it's running.

1. Clone the Repository
git clone <your-repository-url>
cd MoSPI-Scraper-RAG-chatbot

2. Create requirements.txt
Ensure you have a requirements.txt file in your project root with the following minimal dependencies to avoid issues like torch downloads:

# requirements.txt
# --- RAG Core Dependencies ---
sentence-transformers
numpy
faiss-cpu==1.7.4 # Use this specific version to avoid torch dependency
ollama

# --- API & UI Frameworks ---
fastapi
uvicorn
streamlit

3. Build & Run Docker Containers
This command will build the Docker images and start all the services (Ollama, pipeline, API, UI).

Note for PowerShell users: Use ; instead of && to chain commands.

docker compose build --no-cache ; docker compose up

4. Pull the LLM Model into Ollama Container
Once all containers are up, the Ollama container will be running but without a language model. You need to pull one into it. We recommend phi3 for lower resource usage.

For Phi-3 (recommended for lower memory):

docker compose exec ollama ollama pull phi3

For LLaMA 3 (requires more RAM):

docker compose exec ollama ollama pull llama3

5. Run Scraper, Pipeline, and Indexer inside the Container
These steps process your data and build the FAISS index.

Access the pipeline container shell:

docker compose exec pipeline /bin/bash

Execute the scripts (inside the container shell):

python -m scraper.crawl
python -m pipeline.run
python -m rag.index

Wait for each script to complete before running the next. The rag.index script will build your vector index.

Exit the container shell:

exit

6. Access the Chatbot UI
Once all services are running and the index is built, open your web browser and go to:

👉 http://localhost:8501

You should see the Streamlit chatbot interface, ready to answer questions based on your MoSPI data!

💬 Testing the Chatbot
Here are some sample questions you can ask the chatbot:

"What is the unemployment rate for males aged 15-29 in rural areas in June 2025?"

"What is the unemployment rate for females in urban areas in April 2025?"

"What is the document title for the data from June 2025?"

"Compare the unemployment rate for males and females in urban areas in April 2025."

"What is the overall unemployment rate (for all persons) in rural areas in May 2025?"

⚠️ Troubleshooting
unknown flag: --no-cache / InvalidEndOfLine: If you see this error, ensure you are using the correct command separator for your terminal. For PowerShell, use ; instead of &&:

docker compose build --no-cache ; docker compose up

torch download stuck: This indicates faiss-cpu is pulling unnecessary dependencies. Ensure faiss-cpu==1.7.4 is explicitly listed in requirements.txt. Then, use docker compose build --no-cache ; docker compose up to rebuild.

model requires more system memory: Your system does not have enough RAM.

Close all unnecessary applications.

Use a smaller model like phi3 (run docker compose exec ollama ollama pull phi3).

Update rag/api.py to use model='phi3'.

{"detail":"Method Not Allowed"}: You are making a GET request to a POST endpoint. Use the Streamlit UI or a requests script.

Chatbot Hallucinations: The model is generating information not in the context. This is common with smaller models or sub-optimal prompts. We've updated the prompt to mitigate this. Consider using a larger model if resources allow, or further refining the prompt.

API is not running (Frontend error): Ensure your rag_api container is running without errors. Check the Docker logs for the rag_api service: docker compose logs rag_api.

💡 Future Improvements
Enhanced Chunking: Implement more sophisticated text chunking strategies beyond simple fixed-size splits (e.g., semantic chunking, hierarchical chunking).

Advanced Prompt Engineering: Further refine the system prompt to guide the LLM more effectively, especially for complex table extraction and numerical aggregation.

Hybrid Retrieval: Combine vector search with keyword-based search (e.g., BM25) for more robust retrieval.

Caching: Implement caching for LLM responses and document embeddings to speed up repeated queries.

Error Handling & Logging: Improve error handling and structured logging across all services.

Docker Compose Health Checks: Add health checks to docker-compose.yml to ensure services are fully ready before dependent services start.

Persistent Storage for Scraped Data: Use named volumes for /app/data to persist scraped data across container restarts.