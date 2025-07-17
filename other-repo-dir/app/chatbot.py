"""
Main chatbot class that orchestrates document processing, retrieval, and generation.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import time

from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .retriever import Retriever
from .generator import AnswerGenerator
from .config import get_config

logger = logging.getLogger(__name__)

class DocumentChatbot:
    """Main chatbot class for document-based Q&A."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, model_path: Optional[str] = None):
        self.config = config or get_config()
        
        # Initialize components
        self.document_processor = DocumentProcessor(
            chunk_size=self.config["vector_store"]["chunk_size"],
            chunk_overlap=self.config["vector_store"]["chunk_overlap"]
        )
        
        self.vector_store = VectorStore(
            persist_directory=self.config["vector_store"]["persist_directory"],
            collection_name=self.config["vector_store"]["collection_name"]
        )
        
        self.retriever = Retriever(
            vector_store=self.vector_store,
            config=self.config["retrieval"]
        )
        
        self.generator = AnswerGenerator(
            model_path=model_path,
            config=self.config["llm"]
        )
        
        logger.info("DocumentChatbot initialized successfully")
    
    def ingest_documents(self, folder_path: str) -> Dict[str, Any]:
        """Ingest documents from a folder."""
        start_time = time.time()
        
        try:
            # Process documents
            logger.info(f"Processing documents from: {folder_path}")
            chunks = self.document_processor.process_folder(folder_path)
            
            if not chunks:
                return {
                    "success": False,
                    "message": "No supported documents found in the folder",
                    "stats": {"total_chunks": 0, "processing_time": 0}
                }
            
            # Add to vector store
            logger.info(f"Adding {len(chunks)} chunks to vector store")
            self.vector_store.add_documents(chunks)
            
            processing_time = time.time() - start_time
            
            # Get stats
            stats = self.vector_store.get_collection_stats()
            stats.update({
                "new_chunks": len(chunks),
                "processing_time": processing_time
            })
            
            return {
                "success": True,
                "message": f"Successfully processed {len(chunks)} chunks",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            return {
                "success": False,
                "message": f"Error processing documents: {str(e)}",
                "stats": {"total_chunks": 0, "processing_time": 0}
            }
    
    def ask_question(self, question: str, k: Optional[int] = None) -> Dict[str, Any]:
        """Ask a question and get an answer."""
        start_time = time.time()
        
        try:
            # Retrieve relevant documents
            retrieval_results = self.retriever.retrieve(question, k=k)
            
            # Check if we have sufficient results
            if not retrieval_results:
                return {
                    "answer": "I don't know. I couldn't find any relevant information in the documents.",
                    "confidence": 0.0,
                    "citations": [],
                    "sources": [],
                    "retrieval_results": [],
                    "total_time": time.time() - start_time
                }
            
            # Check retrieval confidence
            if not self.retriever.check_retrieval_confidence(retrieval_results):
                return {
                    "answer": "I don't know. The available information doesn't seem directly relevant to your question.",
                    "confidence": 0.0,
                    "citations": [],
                    "sources": [],
                    "retrieval_results": [],
                    "total_time": time.time() - start_time
                }
            
            # Generate answer
            generation_result = self.generator.generate_answer(question, retrieval_results)
            
            # Combine results
            total_time = time.time() - start_time
            
            return {
                "answer": generation_result["answer"],
                "confidence": generation_result["confidence"],
                "citations": generation_result["citations"],
                "sources": generation_result["sources"],
                "retrieval_results": [
                    {
                        "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                        "source": Path(r.source).name,
                        "page": r.page_number,
                        "score": round(r.similarity_score, 3)
                    }
                    for r in retrieval_results[:3]
                ],
                "total_time": total_time,
                "generation_time": generation_result["generation_time"]
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question.",
                "confidence": 0.0,
                "citations": [],
                "sources": [],
                "retrieval_results": [],
                "total_time": time.time() - start_time,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        vector_stats = self.vector_store.get_collection_stats()
        
        return {
            "vector_store": vector_stats,
            "config": {
                "chunk_size": self.config["vector_store"]["chunk_size"],
                "chunk_overlap": self.config["vector_store"]["chunk_overlap"],
                "retrieval_k": self.config["retrieval"]["k"],
                "confidence_threshold": self.config["retrieval"]["confidence_threshold"]
            }
        }
    
    def reset_knowledge_base(self) -> Dict[str, Any]:
        """Reset the knowledge base (delete all documents)."""
        try:
            self.vector_store.reset_collection()
            return {
                "success": True,
                "message": "Knowledge base reset successfully"
            }
        except Exception as e:
            logger.error(f"Error resetting knowledge base: {e}")
            return {
                "success": False,
                "message": f"Error resetting knowledge base: {str(e)}"
            }
    
    def search_documents(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search documents without generating an answer."""
        try:
            results = self.retriever.retrieve(query, k=k)
            
            return [
                {
                    "content": result.content,
                    "source": Path(result.source).name,
                    "page": result.page_number,
                    "similarity_score": round(result.similarity_score, 3),
                    "citations": result.citations
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_available_sources(self) -> List[str]:
        """Get list of available document sources."""
        try:
            # Search for any document to get source list
            dummy_results = self.retriever.retrieve("dummy", k=100)
            sources = self.retriever.get_unique_sources(dummy_results)
            return sources
        except Exception as e:
            logger.error(f"Error getting available sources: {e}")
            return []
