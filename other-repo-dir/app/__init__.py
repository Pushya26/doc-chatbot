"""
Document Chatbot Package
A chatbot system that answers questions from uploaded document collections.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from .retriever import Retriever
from .generator import AnswerGenerator
from .chatbot import DocumentChatbot

__all__ = [
    "DocumentProcessor",
    "VectorStore", 
    "Retriever",
    "AnswerGenerator",
    "DocumentChatbot"
]
