"""
Test suite for the document chatbot system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.chatbot import DocumentChatbot
from app.document_processor import DocumentProcessor
from app.vector_store import VectorStore
from app.config import get_config

class TestDocumentProcessor:
    """Test the document processor."""
    
    def test_text_file_processing(self):
        """Test processing of text files."""
        processor = DocumentProcessor()
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document. It contains multiple sentences. Each sentence should be processed correctly.")
            temp_file = f.name
        
        try:
            chunks = processor.process_file(temp_file)
            assert len(chunks) > 0
            assert chunks[0].content
            assert chunks[0].source == temp_file
            assert chunks[0].page_number == 1
        finally:
            Path(temp_file).unlink()
    
    def test_markdown_file_processing(self):
        """Test processing of markdown files."""
        processor = DocumentProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a **test** document with _formatting_.\n\n## Section 2\n\nMore content here.")
            temp_file = f.name
        
        try:
            chunks = processor.process_file(temp_file)
            assert len(chunks) > 0
            assert "Test Document" in chunks[0].content
        finally:
            Path(temp_file).unlink()
    
    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        processor = DocumentProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("This is an unsupported file type.")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                processor.process_file(temp_file)
        finally:
            Path(temp_file).unlink()

class TestVectorStore:
    """Test the vector store functionality."""
    
    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(persist_directory=temp_dir)
            assert vector_store.collection is not None
            
            stats = vector_store.get_collection_stats()
            assert "total_documents" in stats

class TestDocumentChatbot:
    """Test the main chatbot functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_folder = Path(self.temp_dir) / "test_docs"
        self.test_folder.mkdir()
        
        # Create test documents
        self.create_test_documents()
        
        # Initialize chatbot with test configuration
        config = get_config()
        config["vector_store"]["persist_directory"] = str(Path(self.temp_dir) / "test_chroma")
        self.chatbot = DocumentChatbot(config=config)
    
    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_documents(self):
        """Create test documents for testing."""
        # Text document
        with open(self.test_folder / "test.txt", 'w') as f:
            f.write("Machine learning is a subset of artificial intelligence. It focuses on the development of algorithms that can learn and make decisions from data.")
        
        # Markdown document
        with open(self.test_folder / "test.md", 'w') as f:
            f.write("# Machine Learning Guide\n\nMachine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning.")
    
    def test_document_ingestion(self):
        """Test document ingestion."""
        result = self.chatbot.ingest_documents(str(self.test_folder))
        
        assert result["success"] is True
        assert result["stats"]["new_chunks"] > 0
        
        # Check that documents are in the vector store
        stats = self.chatbot.get_stats()
        assert stats["vector_store"]["total_documents"] > 0
    
    def test_question_answering(self):
        """Test question answering functionality."""
        # First ingest documents
        self.chatbot.ingest_documents(str(self.test_folder))
        
        # Ask a question
        result = self.chatbot.ask_question("What is machine learning?")
        
        assert "answer" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], float)
        assert result["confidence"] >= 0.0
        assert result["total_time"] > 0
    
    def test_answer_refusal(self):
        """Test that the system refuses to answer when no relevant information is found."""
        # First ingest documents
        self.chatbot.ingest_documents(str(self.test_folder))
        
        # Ask an unrelated question
        result = self.chatbot.ask_question("What is the weather like today?")
        
        # Should have low confidence or explicit refusal
        assert result["confidence"] < 0.5 or "don't know" in result["answer"].lower()
    
    def test_reset_knowledge_base(self):
        """Test resetting the knowledge base."""
        # First ingest documents
        self.chatbot.ingest_documents(str(self.test_folder))
        
        # Verify documents exist
        stats = self.chatbot.get_stats()
        assert stats["vector_store"]["total_documents"] > 0
        
        # Reset knowledge base
        result = self.chatbot.reset_knowledge_base()
        assert result["success"] is True
        
        # Verify documents are gone
        stats = self.chatbot.get_stats()
        assert stats["vector_store"]["total_documents"] == 0
    
    def test_search_documents(self):
        """Test document search functionality."""
        # First ingest documents
        self.chatbot.ingest_documents(str(self.test_folder))
        
        # Search for documents
        results = self.chatbot.search_documents("machine learning", k=5)
        
        assert isinstance(results, list)
        if results:  # If we have results
            assert "content" in results[0]
            assert "similarity_score" in results[0]

def run_basic_tests():
    """Run basic tests without pytest."""
    print("🧪 Running Basic Tests")
    print("=" * 30)
    
    try:
        # Test 1: Document processor
        print("1. Testing document processor...")
        processor = DocumentProcessor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for basic testing.")
            temp_file = f.name
        
        chunks = processor.process_file(temp_file)
        assert len(chunks) > 0, "Document processor failed"
        Path(temp_file).unlink()
        print("   ✅ Document processor test passed")
        
        # Test 2: Vector store
        print("2. Testing vector store...")
        with tempfile.TemporaryDirectory() as temp_dir:
            vector_store = VectorStore(persist_directory=temp_dir)
            stats = vector_store.get_collection_stats()
            assert "total_documents" in stats, "Vector store failed"
        print("   ✅ Vector store test passed")
        
        # Test 3: End-to-end basic test
        print("3. Testing basic end-to-end functionality...")
        with tempfile.TemporaryDirectory() as temp_dir:
            config = get_config()
            config["vector_store"]["persist_directory"] = str(Path(temp_dir) / "test_chroma")
            chatbot = DocumentChatbot(config=config)
            
            # Create test document
            test_folder = Path(temp_dir) / "docs"
            test_folder.mkdir()
            with open(test_folder / "test.txt", 'w') as f:
                f.write("Machine learning is a type of artificial intelligence.")
            
            # Test ingestion
            result = chatbot.ingest_documents(str(test_folder))
            assert result["success"], "Document ingestion failed"
            
            # Test question answering
            answer = chatbot.ask_question("What is machine learning?")
            assert "answer" in answer, "Question answering failed"
            
        print("   ✅ End-to-end test passed")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    run_basic_tests()
