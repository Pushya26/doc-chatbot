"""
Answer generation module using language models.
"""

import logging
from typing import List, Dict, Any, Optional
import re
import time

try:
    from langchain_community.llms import LlamaCpp
    from langchain_core.callbacks.manager import CallbackManager
    from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
except ImportError:
    try:
        from langchain.llms import LlamaCpp
        from langchain.callbacks.manager import CallbackManager
        from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    except ImportError:
        # Fallback - will disable LLM functionality
        LlamaCpp = None
        CallbackManager = None
        StreamingStdOutCallbackHandler = None

from .retriever import RetrievalResult
from .config import LLM_CONFIG, CITATION_CONFIG

logger = logging.getLogger(__name__)

class AnswerGenerator:
    """Generates answers using retrieved context and language models."""
    
    def __init__(self, model_path: Optional[str] = None, config: Dict[str, Any] = None):
        self.config = config or LLM_CONFIG
        self.citation_config = CITATION_CONFIG
        
        # Initialize LLM if model path is provided
        self.llm = None
        if model_path:
            self._initialize_llm(model_path)
    
    def _initialize_llm(self, model_path: str) -> None:
        """Initialize the language model."""
        try:
            callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
            
            self.llm = LlamaCpp(
                model_path=model_path,
                max_tokens=self.config.get("max_tokens", 500),
                temperature=self.config.get("temperature", 0.1),
                n_ctx=self.config.get("n_ctx", 2048),
                n_batch=self.config.get("n_batch", 512),
                n_gpu_layers=self.config.get("n_gpu_layers", 0),
                callback_manager=callback_manager,
                verbose=False
            )
            logger.info("Language model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize language model: {e}")
            self.llm = None
    
    def generate_answer(
        self, 
        query: str, 
        retrieval_results: List[RetrievalResult],
        include_citations: bool = True
    ) -> Dict[str, Any]:
        """Generate an answer based on query and retrieved context."""
        start_time = time.time()
        
        # Check if we have sufficient context
        if not retrieval_results:
            return {
                "answer": "I don't know. I couldn't find relevant information in the provided documents.",
                "confidence": 0.0,
                "citations": [],
                "sources": [],
                "generation_time": time.time() - start_time
            }
        
        # Check confidence threshold
        avg_confidence = sum(r.similarity_score for r in retrieval_results) / len(retrieval_results)
        if avg_confidence < 0.3:  # Low confidence threshold
            return {
                "answer": "I don't know. The available information doesn't seem directly relevant to your question.",
                "confidence": avg_confidence,
                "citations": [],
                "sources": [],
                "generation_time": time.time() - start_time
            }
        
        # Prepare context
        context = self._prepare_context(retrieval_results)
        
        # Generate answer
        if self.llm:
            answer = self._generate_with_llm(query, context)
        else:
            answer = self._generate_simple_answer(query, retrieval_results)
        
        # Add citations if requested
        if include_citations:
            answer = self._add_citations(answer, retrieval_results)
        
        # Collect sources
        sources = list(set(r.source for r in retrieval_results))
        citations = []
        for result in retrieval_results[:self.citation_config.get("max_citations", 3)]:
            citations.extend(result.citations)
        
        generation_time = time.time() - start_time
        
        return {
            "answer": answer,
            "confidence": avg_confidence,
            "citations": citations,
            "sources": sources,
            "generation_time": generation_time
        }
    
    def _prepare_context(self, retrieval_results: List[RetrievalResult]) -> str:
        """Prepare context from retrieval results."""
        context_parts = []
        
        for i, result in enumerate(retrieval_results[:5], 1):  # Limit to top 5 results
            citation = ", ".join(result.citations)
            context_part = f"Context {i} {citation}:\n{result.content}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _generate_with_llm(self, query: str, context: str) -> str:
        """Generate answer using the language model."""
        prompt = self._create_prompt(query, context)
        
        try:
            response = self.llm(prompt)
            
            # Clean up the response
            answer = self._clean_response(response)
            
            # Ensure answer length limit
            max_words = 500
            words = answer.split()
            if len(words) > max_words:
                answer = " ".join(words[:max_words]) + "..."
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer with LLM: {e}")
            return "I apologize, but I encountered an error while generating the answer."
    
    def _generate_simple_answer(self, query: str, retrieval_results: List[RetrievalResult]) -> str:
        """Generate a simple answer without LLM (fallback)."""
        # Simple extractive approach - find the most relevant sentence
        best_result = retrieval_results[0]
        content = best_result.content
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Find sentences that contain query keywords
        query_words = set(query.lower().split())
        best_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                sentence_words = set(sentence.lower().split())
                overlap = len(query_words & sentence_words)
                if overlap > 0:
                    best_sentences.append((sentence, overlap))
        
        # Sort by overlap and take top sentences
        best_sentences.sort(key=lambda x: x[1], reverse=True)
        
        if best_sentences:
            answer_parts = [sent[0] for sent in best_sentences[:3]]
            answer = ". ".join(answer_parts)
            if not answer.endswith('.'):
                answer += "."
            return answer
        else:
            return f"Based on the documents, here's what I found: {content[:300]}..."
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create a prompt for the language model."""
        prompt = f"""You are a helpful assistant that answers questions based only on the provided context. 
        
Instructions:
- Answer the question using only information from the context provided
- If the context doesn't contain enough information to answer the question, say "I don't know"
- Keep your answer concise and under 500 words
- Be accurate and don't make up information
- Include specific details when available

Context:
{context}

Question: {query}

Answer:"""
        
        return prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean up the model response."""
        # Remove common artifacts
        response = response.strip()
        
        # Remove repeated patterns
        lines = response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in cleaned_lines[-3:]:  # Avoid recent repetitions
                cleaned_lines.append(line)
        
        cleaned_response = ' '.join(cleaned_lines)
        
        # Remove excessive whitespace
        cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
        
        return cleaned_response
    
    def _add_citations(self, answer: str, retrieval_results: List[RetrievalResult]) -> str:
        """Add inline citations to the answer."""
        if not self.citation_config.get("include_page_numbers", True):
            return answer
        
        # Get unique citations
        citations = []
        for result in retrieval_results[:self.citation_config.get("max_citations", 3)]:
            citations.extend(result.citations)
        
        unique_citations = list(dict.fromkeys(citations))  # Preserve order, remove duplicates
        
        if unique_citations:
            citation_text = " " + ", ".join(unique_citations)
            return answer + citation_text
        
        return answer
