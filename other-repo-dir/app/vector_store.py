"""
Vector store module for managing document embeddings using ChromaDB.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings

import numpy as np

from .document_processor import DocumentChunk
from .config import VECTOR_STORE_CONFIG, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages document embeddings and similarity search using ChromaDB."""
    
    def __init__(self, persist_directory: str = None, collection_name: str = "documents"):
        self.persist_directory = persist_directory or VECTOR_STORE_CONFIG["persist_directory"]
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:  # Collection doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for Q&A system"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks to the vector store."""
        if not chunks:
            logger.warning("No chunks provided to add to vector store")
            return
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk.content)
            
            # Prepare metadata
            metadata = chunk.metadata.copy()
            metadata.update({
                "source": chunk.source,
                "chunk_id": chunk.chunk_id or f"chunk_{i}",
                "page_number": chunk.page_number or 1
            })
            metadatas.append(metadata)
            ids.append(chunk.chunk_id or f"chunk_{i}")
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        embeddings = self.embeddings.embed_documents(documents)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        confidence_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Perform similarity search and return relevant chunks."""
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Process results
        relevant_chunks = []
        
        if results["documents"] and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            
            for doc, metadata, distance in zip(documents, metadatas, distances):
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                similarity_score = 1 / (1 + distance)
                
                if similarity_score >= confidence_threshold:
                    relevant_chunks.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": similarity_score,
                        "distance": distance
                    })
        
        logger.info(f"Found {len(relevant_chunks)} relevant chunks for query")
        return relevant_chunks
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }
    
    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")
    
    def reset_collection(self) -> None:
        """Reset the collection (delete and recreate)."""
        try:
            self.delete_collection()
        except ValueError:
            pass  # Collection doesn't exist
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Document chunks for Q&A system"}
        )
        logger.info(f"Reset collection: {self.collection_name}")
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any], k: int = 10) -> List[Dict[str, Any]]:
        """Search documents by metadata filters."""
        # Convert metadata filter to ChromaDB where clause
        where_clause = {}
        for key, value in metadata_filter.items():
            where_clause[key] = {"$eq": value}
        
        results = self.collection.get(
            where=where_clause,
            limit=k,
            include=["documents", "metadatas"]
        )
        
        documents = []
        if results["documents"]:
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                documents.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1.0  # No similarity calculation for metadata search
                })
        
        return documents
