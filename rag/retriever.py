# Retrieval logic (embedding, vector search)

# rag/retriever.py

import os
import faiss
import json
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """
    A class to retrieve relevant document chunks using a pre-built FAISS index.
    """
    def __init__(self, index_path: str, metadata_path: str, model_name: str = "all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.model_name = model_name
        self.model = None
        self.index = None
        self.metadata = None
        self._load_components()

    def _load_components(self):
        """Loads the Sentence Transformer model, FAISS index, and metadata."""
        logger.info("Loading Sentence Transformer model...")
        self.model = SentenceTransformer(self.model_name)
        
        logger.info(f"Loading FAISS index from {self.index_path}")
        self.index = faiss.read_index(self.index_path)
        
        logger.info(f"Loading metadata from {self.metadata_path}")
        with open(self.metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        logger.info("Retriever components loaded successfully.")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Takes a query and returns the most relevant document chunks.
        
        Args:
            query (str): The user's search query.
            top_k (int): The number of top results to retrieve.
        
        Returns:
            List[Dict]: A list of dictionaries containing the relevant chunk metadata.
        """
        if not self.index or not self.model or not self.metadata:
            logger.error("Retriever is not properly initialized.")
            return []

        # Convert the query to an embedding
        query_embedding = self.model.encode(query)
        query_embedding_np = np.array([query_embedding]).astype('float32')
        
        # Search the FAISS index
        distances, indices = self.index.search(query_embedding_np, top_k)
        
        retrieved_chunks = []
        for i in indices[0]:
            if i >= 0 and i < len(self.metadata):
                chunk_data = self.metadata[i]
                retrieved_chunks.append(chunk_data)
        
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks.")
        return retrieved_chunks

if __name__ == '__main__':
    # This is an example of how to use the retriever
    INDEX_PATH = os.path.join("data", "rag", "faiss_index.bin")
    METADATA_PATH = os.path.join("data", "rag", "faiss_index_metadata.json")
    
    if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
        retriever = DocumentRetriever(INDEX_PATH, METADATA_PATH)
        query = "What is the unemployment rate in rural areas?"
        results = retriever.retrieve(query, top_k=3)
        print("\n--- Retrieved Chunks ---")
        for i, result in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Document Title: {result.get('document_title')}")
            print(f"  Chunk: {result.get('chunk_text')}\n")
    else:
        logger.error("FAISS index files not found. Please run the indexing script first.")