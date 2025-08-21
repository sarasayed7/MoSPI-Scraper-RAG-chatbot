# FastAPI/Flask API endpoints for the chatbot [cite: 82]

# rag/api.py

import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from rag.retriever import DocumentRetriever
import ollama

logger = logging.getLogger(__name__)

# Load the retriever
INDEX_PATH = os.path.join("data", "rag", "faiss_index.bin")
METADATA_PATH = os.path.join("data", "rag", "faiss_index_metadata.json")

if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
    raise RuntimeError("FAISS index files not found. Please run rag/index.py first.")

retriever = DocumentRetriever(INDEX_PATH, METADATA_PATH)

app = FastAPI(
    title="MoSPI RAG Chatbot API",
    description="API for a chatbot that answers questions based on MoSPI documents."
)

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    """Endpoint to check if the API is running."""
    return {"status": "ok"}

@app.post("/query")
def answer_query(request: QueryRequest):
    """
    Answers a user query using the RAG system and the local LLaMA 3 model.
    """
    try:
        # 1. Retrieve relevant context from the FAISS index
        context_chunks = retriever.retrieve(request.query)
        
        if not context_chunks:
            return {"answer": "I could not find any relevant information to answer your question."}
        
        context = "\n".join([chunk["chunk_text"] for chunk in context_chunks])
        
        # 2. Prepare the prompt for the LLM
        prompt = f"""
        You are a helpful assistant that answers questions based on the provided context.
        If the answer is not in the context, say that you don't know.
        
        Context:
        {context}
        
        Question: {request.query}
        """
        
        # 3. Call the local LLaMA 3 model via Ollama
        logger.info("Calling Ollama API with LLaMA 3 model...")
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
        )
        
        answer = response.get('message', {}).get('content', 'An error occurred while getting the response from the LLM.')
        
        return {"answer": answer}
        
    except Exception as e:
        logger.error(f"An error occurred during query processing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")