# MoSPI Data Scraper & LLaMA-powered Q&A Chatbot 🤖

This project builds a comprehensive data pipeline and a Retrieval-Augmented Generation (RAG) chatbot. It's designed to:
1.  **Scrape** public statistical content from the Ministry of Statistics and Programme Implementation (MoSPI) website.
2.  **Process** the collected data, including text and tables from PDFs.
3.  **Answer questions** about the scraped corpus using a local LLaMA 3 model, providing contextual and cited responses.

---

## **0) Overview**

The core goal is to demonstrate data engineering, web scraping, ETL design, data modeling, reproducibility, LLM integration, and product thinking. The system is containerized using Docker and Docker Compose for easy setup and execution.

---

## **1) Deliverables**

* [X] **Code Repository:** Organized into `/scraper`, `/pipeline`, `/rag`, and `/infra` directories.
* [X] **`README.md`:** This file serves as the setup guide, documentation for architecture, trade-offs, and future improvements.
* [X] **`.env.example`:** Template for configurable settings.
* [ ] **Tests:** (Unit and Integration tests are planned but not fully implemented in this version).
* [X] **Data Artifacts:** Generated a FAISS vector index from processed documents.
* [X] **Runnable Demo:** The entire system (`ollama`, `scraper`, `pipeline`, `rag_api`, `rag_ui`) can be brought up using `docker compose up`.
* [ ] **(Optional, Bonus)** A 2-3 minute screen-recording demo.

---

## **2) Setup & Installation**

To run this project, you need **Docker** and **Docker Compose** installed on your machine.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo.git](https://github.com/your-username/your-repo.git)
    cd your-repo
    ```

2.  **Set up environment variables:**
    * Create a `.env` file in the root directory from the `.env.example` template. Populate it with any necessary configuration settings (e.g., `OLLAMA_HOST` is handled in `docker-compose.yml`, but other scraper-specific settings might go here).

3.  **Pull the LLaMA model into Ollama container:**
    * The `ollama` service will be started by `docker compose up`. After the containers are running, you need to pull the language model into the Ollama container.
    * Open a **new terminal** and run:
        ```bash
        docker compose exec ollama ollama pull llama3
        ```
    * **Note on Memory**: The default `llama3` model is ~4.7 GB and requires significant RAM. If you face `model requires more system memory` errors, you can use a smaller, quantized version like `llama3:8b-instruct-q3_K_M`.
        * To pull a smaller model: `docker compose exec ollama ollama pull llama3:8b-instruct-q3_K_M`
        * You would then need to **edit `rag/api.py`** to change `model='llama3'` to `model='llama3:8b-instruct-q3_K_M'`.

---

## **3) Running the Project**

Follow these steps to build, run, and interact with the chatbot.

1.  **Build and run the Docker containers:**
    * This command builds the Docker images without using the cache and then starts all the services defined in `docker-compose.yml`.
    * **For PowerShell users:**
        ```powershell
        docker compose build --no-cache ; docker compose up
        ```
    * **For Bash/Zsh (Linux/macOS/Git Bash) users:**
        ```bash
        docker compose build --no-cache && docker compose up
        ```

2.  **Execute the data pipelines inside the `pipeline` container:**
    * Once the `docker compose up` command finishes and all services are running, open a **new terminal**.
    * Start a shell session inside the `pipeline` container:
        ```bash
        docker compose exec pipeline /bin/bash
        ```
    * Inside the container's shell, run the scraping, ETL, and indexing scripts in order:
        ```bash
        python -m scraper.crawl
        python -m pipeline.run
        python -m rag.index
        exit # To exit the container's shell
        ```
    * **Note**: The first run of `scraper.crawl` will download PDFs to `./data/raw/pdf`. Ensure you have internet connectivity.

3.  **Access the web UI:**
    * Once the `rag.index` script has completed successfully, your chatbot is fully operational.
    * Open your web browser and navigate to: **`http://localhost:8501`**.

---

## **4) Project Structure**

<img width="479" height="623" alt="image" src="https://github.com/user-attachments/assets/6e9be5c5-ebbb-4640-96a6-aec167314451" />

---

## **5) Architecture & Trade-offs**

This project employs a modular, containerized architecture designed for reproducibility and maintainability.

* **Containerization (Docker & Docker Compose):** Each core component (Ollama, Scraper/Pipeline, FastAPI API, Streamlit UI) runs in its own Docker container. This ensures consistent environments across different machines and simplifies dependency management.
* **Data Flow:**
    1.  **Scraper (`scraper.crawl`):** Collects document metadata and PDF links from the MoSPI website.
    2.  **PDF Parser (`scraper.parse`):** Downloads and extracts text/tables from PDFs.
    3.  **ETL Pipeline (`pipeline.run`):** Processes raw data, chunks text, and stores processed documents.
    4.  **Indexer (`rag.index`):** Creates a FAISS vector index from the processed text chunks.
    5.  **RAG API (`rag.api`):** A FastAPI server that receives user queries, retrieves relevant context from the FAISS index, and prompts a local LLaMA 3 model via the Ollama container.
    6.  **Frontend (`app.py`):** A Streamlit application providing an interactive chat interface.
* **LLM Integration:** Utilizes Ollama to run large language models locally, reducing API costs and enhancing data privacy.
* **Vector Store:** FAISS is used for efficient similarity search to retrieve the most relevant document chunks.
* **Prompt Engineering:** Prompts are crafted to instruct the LLM to answer strictly from the provided context, including document titles, to minimize hallucinations.

**Key Trade-offs:**

* **Local LLM vs. Cloud API:** Chose local Ollama for cost efficiency and self-containment, despite higher local resource demands.
* **Quantized Models:** Required using smaller, quantized LLaMA 3 models (e.g., `phi3` or `llama3:8b-instruct-q3_K_M`) due to host machine memory constraints, which can sometimes impact answer quality compared to larger models.
* **Text-based Table Processing:** The PDF parser extracts tables as text, which can sometimes challenge smaller LLMs in interpreting structured data, leading to occasional inaccuracies or verbose responses.

---

## **6) Future Improvements**

* **Advanced Chunking Strategies:** Implement more sophisticated text-chunking (e.g., recursive text splitting, semantic chunking, or table-aware chunking) to improve retrieval accuracy.
* **Enhanced Citation Generation:** Implement more precise citations, potentially linking to page numbers or specific table references within the source PDFs.
* **Hybrid Retrieval:** Combine vector search with keyword-based search (e.g., BM25) for a more robust retrieval mechanism.
* **Comprehensive Testing:** Expand unit and integration tests to cover all components and ensure data quality at each stage of the pipeline.
* **Data Validation with Great Expectations:** Integrate a data validation framework like Great Expectations into the ETL pipeline.
* **User Feedback & Evaluation:** Implement a feedback mechanism in the UI to collect user satisfaction and continuously evaluate chatbot performance with a dedicated Q&A dataset.
* **UI Enhancements:** Add features like displaying retrieved source snippets directly in the UI, or toggles for RAG parameters (e.g., `top_k`, temperature).






