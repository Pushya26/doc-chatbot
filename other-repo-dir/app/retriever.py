"""
Retriever module for finding relevant document chunks.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .vector_store import VectorStore
from .config import RETRIEVAL_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    """Represents a retrieval result with content and metadata."""
    content: str
    source: str
    page_number: Optional[int]
    similarity_score: float
    metadata: Dict[str, Any]
    citations: List[str]

class Retriever:
    """Handles document retrieval and relevance scoring."""
    
    def __init__(self, vector_store: VectorStore, config: Dict[str, Any] = None):
        self.vector_store = vector_store
        self.config = config or RETRIEVAL_CONFIG
        
        self.k = self.config.get("k", 5)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.3)
        self.max_tokens_per_chunk = self.config.get("max_tokens_per_chunk", 500)
    
    def retrieve(self, query: str, k: Optional[int] = None) -> List[RetrievalResult]:
        """Retrieve relevant document chunks for a query."""
        k = k or self.k
        
        # Perform similarity search
        raw_results = self.vector_store.similarity_search(
            query=query,
            k=k,
            confidence_threshold=self.confidence_threshold
        )
        
        # Process and filter results
        results = []
        seen_content = set()  # Avoid duplicate content
        
        for raw_result in raw_results:
            content = raw_result["content"]
            metadata = raw_result["metadata"]
            similarity_score = raw_result["similarity_score"]
            
            # Skip duplicates
            content_hash = hash(content)
            if content_hash in seen_content:
                continue
            seen_content.add(content_hash)
            
            # Create citation
            citations = self._create_citations(metadata)
            
            # Create result
            result = RetrievalResult(
                content=content,
                source=metadata.get("source", "Unknown"),
                page_number=metadata.get("page_number"),
                similarity_score=similarity_score,
                metadata=metadata,
                citations=citations
            )
            
            results.append(result)
        
        # Sort by similarity score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        logger.info(f"Retrieved {len(results)} relevant chunks")
        return results
    
    def _create_citations(self, metadata: Dict[str, Any]) -> List[str]:
        """Create citation strings from metadata."""
        citations = []
        
        file_name = metadata.get("file_name", metadata.get("source", "Unknown"))
        page_number = metadata.get("page_number") or metadata.get("page")
        
        if page_number:
            citation = f"[{file_name}, page {page_number}]"
        else:
            citation = f"[{file_name}]"
        
        citations.append(citation)
        return citations
    
    def check_retrieval_confidence(self, results: List[RetrievalResult]) -> bool:
        """Check if retrieval results meet confidence threshold."""
        if not results:
            return False
        
        # Check if the best result meets the threshold
        best_score = results[0].similarity_score
        return best_score >= self.confidence_threshold
    
    def get_context_for_generation(self, results: List[RetrievalResult]) -> str:
        """Combine retrieval results into context for answer generation."""
        if not results:
            return ""
        
        context_parts = []
        total_tokens = 0
        
        for i, result in enumerate(results):
            # Estimate token count (rough approximation: 1 token ≈ 4 characters)
            chunk_tokens = len(result.content) // 4
            
            if total_tokens + chunk_tokens > self.max_tokens_per_chunk * len(results):
                break
            
            # Add chunk with citation
            chunk_text = f"Source {i+1}: {result.content}\nCitation: {', '.join(result.citations)}\n"
            context_parts.append(chunk_text)
            total_tokens += chunk_tokens
        
        return "\n---\n".join(context_parts)
    
    def filter_by_source(self, results: List[RetrievalResult], source_filter: str) -> List[RetrievalResult]:
        """Filter results by source file."""
        filtered = [r for r in results if source_filter.lower() in r.source.lower()]
        logger.info(f"Filtered to {len(filtered)} results from source: {source_filter}")
        return filtered
    
    def get_unique_sources(self, results: List[RetrievalResult]) -> List[str]:
        """Get list of unique sources from results."""
        sources = set()
        for result in results:
            if result.metadata.get("file_name"):
                sources.add(result.metadata["file_name"])
        return sorted(list(sources))
