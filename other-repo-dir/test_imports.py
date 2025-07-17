#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

try:
    print("Testing imports...")
    
    # Test PDF processing
    import PyPDF2
    print("✓ PyPDF2 imported successfully")
    
    import pdfplumber
    print("✓ pdfplumber imported successfully")
    
    # Test LangChain components
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("✓ LangChain text splitter imported successfully")
    
    # Test embeddings
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✓ HuggingFace embeddings imported successfully")
    
    # Test ChromaDB
    import chromadb
    print("✓ ChromaDB imported successfully")
    
    # Test our app components
    from app.document_processor import DocumentProcessor
    print("✓ DocumentProcessor imported successfully")
    
    from app.vector_store import VectorStore
    print("✓ VectorStore imported successfully")
    
    from app.chatbot import DocumentChatbot
    print("✓ DocumentChatbot imported successfully")
    
    print("\n🎉 All imports successful! The system should work correctly now.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
