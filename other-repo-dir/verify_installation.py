"""
Simple test script to verify the installation works.
"""

import sys
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all the important imports."""
    print("🔍 Testing imports...")
    
    try:
        print("  Testing basic imports...")
        import streamlit
        import numpy
        import pandas
        print("  ✅ Basic packages imported successfully")
        
        print("  Testing LangChain imports...")
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            print("  ✅ LangChain community imports work")
        except ImportError:
            from langchain.embeddings import HuggingFaceEmbeddings
            print("  ✅ LangChain legacy imports work")
        
        print("  Testing ChromaDB import...")
        import chromadb
        print("  ✅ ChromaDB imported successfully")
        
        print("  Testing app modules...")
        from app.config import get_config
        from app.document_processor import DocumentProcessor
        from app.vector_store import VectorStore
        from app.retriever import Retriever
        from app.generator import AnswerGenerator
        from app.chatbot import DocumentChatbot
        print("  ✅ All app modules imported successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Import here to ensure it's available
        from app.config import get_config
        from app.document_processor import DocumentProcessor
        from app.vector_store import VectorStore
        from app.chatbot import DocumentChatbot
        
        # Test configuration
        config = get_config()
        print("  ✅ Configuration loaded")
        
        # Test document processor
        processor = DocumentProcessor()
        print("  ✅ Document processor created")
        
        # Test vector store (without persistence)
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(persist_directory=temp_dir)
            print("  ✅ Vector store created")
        
        # Test chatbot initialization
        config["vector_store"]["persist_directory"] = str(Path(tempfile.gettempdir()) / "test_chroma")
        chatbot = DocumentChatbot(config=config)
        print("  ✅ Chatbot initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    print("🎯 Running Installation Verification Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test basic functionality
        functionality_ok = test_basic_functionality()
        
        if functionality_ok:
            print("\n🎉 All tests passed! Your installation is working correctly.")
            print("\n🚀 Next steps:")
            print("  1. Add documents to the 'data' folder")
            print("  2. Run: python main.py ingest data --reset")
            print("  3. Run: python main.py ask 'Your question here'")
            print("  4. Or try: streamlit run streamlit_app.py")
            return True
        else:
            print("\n❌ Functionality tests failed")
            return False
    else:
        print("\n❌ Import tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
