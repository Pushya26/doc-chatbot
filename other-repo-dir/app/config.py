"""
Configuration settings for the document chatbot system.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"
MODELS_DIR = BASE_DIR / "models"

# Embedding model configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"  # or "cuda" if GPU available

# Vector store configuration
VECTOR_STORE_CONFIG = {
    "persist_directory": str(CHROMA_DB_DIR),
    "collection_name": "documents",
    "chunk_size": 1000,
    "chunk_overlap": 200
}

# Retrieval configuration
RETRIEVAL_CONFIG = {
    "k": 5,  # Number of chunks to retrieve
    "confidence_threshold": 0.3,  # Minimum similarity score
    "max_tokens_per_chunk": 500
}

# LLM configuration
LLM_CONFIG = {
    "model_name": "llama-2-7b-chat",
    "max_tokens": 500,
    "temperature": 0.1,
    "n_ctx": 2048,
    "n_batch": 512,
    "n_gpu_layers": 0  # Adjust based on GPU
}

# Supported file types
SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".txt": "text", 
    ".md": "markdown",
    ".docx": "docx"
}

# Citation configuration
CITATION_CONFIG = {
    "include_page_numbers": True,
    "include_line_numbers": False,
    "max_citations": 3
}

# Performance settings
PERFORMANCE_CONFIG = {
    "max_latency_seconds": 3.0,
    "batch_size": 32,
    "cache_embeddings": True
}

def get_config() -> Dict[str, Any]:
    """Get complete configuration dictionary."""
    return {
        "embedding": {
            "model": EMBEDDING_MODEL,
            "device": EMBEDDING_DEVICE
        },
        "vector_store": VECTOR_STORE_CONFIG,
        "retrieval": RETRIEVAL_CONFIG,
        "llm": LLM_CONFIG,
        "citation": CITATION_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "supported_extensions": SUPPORTED_EXTENSIONS
    }
