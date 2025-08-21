# rag/index.py

import os
import json
import faiss
import numpy as np
import logging
from typing import List, Dict

# Assumed imports for embedding model
from sentence_transformers import SentenceTransformer

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define data and index paths
PROCESSED_DATA_PATH = os.path.join("data", "processed", "processed_documents.json")
FAISS_INDEX_PATH = os.path.join("data", "rag", "faiss_index.bin")

def build_faiss_index(documents: List[Dict], model_name: str = "all-MiniLM-L6-v2"):
    """
    Builds and saves a FAISS vector index from a list of documents.
    Each document is expected to have a 'text_chunks' field.
    """
    logger.info("Loading Sentence Transformer model...")
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        logger.error(f"Failed to load SentenceTransformer model: {e}")
        return

    all_embeddings = []
    chunk_metadata = []

    logger.info("Creating embeddings for all document chunks...")
    for doc in documents:
        for file in doc.get("processed_files", []):
            for i, chunk in enumerate(file.get("text_chunks", [])):
                # Embed the chunk
                try:
                    embedding = model.encode(chunk)
                    all_embeddings.append(embedding)
                    
                    # Store metadata for the chunk
                    chunk_metadata.append({
                        "document_id": doc["id"],
                        "document_title": doc["title"],
                        "chunk_text": chunk,
                        "chunk_index": i
                    })
                except Exception as e:
                    logger.error(f"Failed to create embedding for chunk {i} of document {doc['id']}: {e}")
                    continue

    if not all_embeddings:
        logger.warning("No embeddings created. Index will not be built.")
        return

    # Convert to a NumPy array for FAISS
    embeddings_np = np.array(all_embeddings).astype('float32')
    
    # Build a FAISS index
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    # Save the FAISS index and metadata
    try:
        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(index, FAISS_INDEX_PATH)

        metadata_path = FAISS_INDEX_PATH.replace(".bin", "_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(chunk_metadata, f, indent=4)
            
        logger.info(f"FAISS index built with {index.ntotal} vectors and saved to {FAISS_INDEX_PATH}")
        logger.info(f"Metadata saved to {metadata_path}")
    except Exception as e:
        logger.error(f"Failed to save FAISS index or metadata: {e}")

if __name__ == "__main__":
    if not os.path.exists(PROCESSED_DATA_PATH):
        logger.error("Processed data file not found. Please run the ETL pipeline first.")
    else:
        with open(PROCESSED_DATA_PATH, 'r') as f:
            processed_data = json.load(f)
        build_faiss_index(processed_data)