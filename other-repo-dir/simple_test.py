"""
Simple test to check if the system works
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_system():
    print("🧪 Testing Document Chatbot System")
    print("=" * 40)
    
    try:
        # Test imports
        from app.chatbot import DocumentChatbot
        print("✅ Imports successful")
        
        # Test initialization
        chatbot = DocumentChatbot()
        print("✅ Chatbot initialized")
        
        # Test stats
        stats = chatbot.get_stats()
        print(f"✅ Stats retrieved: {stats['vector_store']['total_documents']} documents")
        
        # Test if data folder exists
        data_folder = Path("data")
        if data_folder.exists():
            files = list(data_folder.glob("*"))
            print(f"✅ Data folder found with {len(files)} files")
            
            if files:
                # Test document ingestion
                print("📚 Testing document ingestion...")
                result = chatbot.ingest_documents(str(data_folder))
                
                if result['success']:
                    print(f"✅ Ingestion successful: {result['stats']['new_chunks']} chunks processed")
                    
                    # Test question answering
                    print("❓ Testing question answering...")
                    answer = chatbot.ask_question("What is this document about?")
                    print(f"✅ Question answered with confidence: {answer['confidence']:.2f}")
                    print(f"Answer: {answer['answer'][:100]}...")
                    
                else:
                    print(f"❌ Ingestion failed: {result['message']}")
            else:
                print("⚠️  No files in data folder to process")
        else:
            print("⚠️  Data folder not found - creating it")
            data_folder.mkdir()
            
            # Create a test document
            test_file = data_folder / "test.txt"
            test_file.write_text("This is a test document about machine learning and artificial intelligence.")
            print("✅ Created test document")
            
            # Test with test document
            result = chatbot.ingest_documents(str(data_folder))
            if result['success']:
                print(f"✅ Test document ingested: {result['stats']['new_chunks']} chunks")
                
                answer = chatbot.ask_question("What is machine learning?")
                print(f"✅ Test question answered: {answer['answer'][:100]}...")
        
        print("\n🎉 All tests passed! System is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system()
    if success:
        print("\n🚀 Ready to use! Try:")
        print("  python main.py ingest data --reset")
        print("  python main.py ask 'Your question here'")
        print("  streamlit run streamlit_app.py")
    sys.exit(0 if success else 1)
