"""
Demo script showcasing the document chatbot functionality.
"""

import sys
import os
from pathlib import Path
import time

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.chatbot import DocumentChatbot

def print_separator(title=""):
    """Print a nice separator."""
    print("\n" + "="*60)
    if title:
        print(f" {title} ".center(60, "="))
        print("="*60)
    print()

def demo_document_ingestion():
    """Demonstrate document ingestion."""
    print_separator("📚 DOCUMENT INGESTION DEMO")
    
    # Initialize chatbot
    print("🤖 Initializing Document Chatbot...")
    chatbot = DocumentChatbot()
    
    # Check if we have the data folder
    data_folder = project_root / "data"
    if not data_folder.exists():
        print(f"❌ Data folder not found at: {data_folder}")
        print("Please ensure you have documents in the 'data' folder")
        return None
    
    # Reset knowledge base
    print("🗑️  Resetting knowledge base...")
    reset_result = chatbot.reset_knowledge_base()
    if reset_result['success']:
        print("✅ Knowledge base reset successfully")
    else:
        print(f"❌ Error: {reset_result['message']}")
        return None
    
    # Ingest documents
    print(f"📥 Ingesting documents from: {data_folder}")
    start_time = time.time()
    
    result = chatbot.ingest_documents(str(data_folder))
    
    if result['success']:
        stats = result['stats']
        print(f"✅ {result['message']}")
        print(f"📊 Statistics:")
        print(f"   - New chunks: {stats.get('new_chunks', 0)}")
        print(f"   - Total documents: {stats.get('total_documents', 0)}")
        print(f"   - Processing time: {stats.get('processing_time', 0):.2f}s")
        return chatbot
    else:
        print(f"❌ {result['message']}")
        return None

def demo_question_answering(chatbot):
    """Demonstrate question answering with example questions."""
    print_separator("❓ QUESTION ANSWERING DEMO")
    
    # Example questions (adjust based on your documents)
    example_questions = [
        "What is machine learning?",
        "What are the key principles mentioned in the document?",
        "Can you summarize the main topics covered?"
    ]
    
    for i, question in enumerate(example_questions, 1):
        print(f"\n🔹 Example Question {i}: {question}")
        print("-" * 50)
        
        start_time = time.time()
        result = chatbot.ask_question(question)
        
        print(f"🤖 Answer:")
        print(result['answer'])
        
        if result['citations']:
            print(f"\n📚 Citations: {', '.join(result['citations'])}")
        
        print(f"\n📊 Confidence: {result['confidence']:.2f}")
        print(f"⏱️  Response time: {result['total_time']:.2f}s")
        
        if result['retrieval_results']:
            print(f"\n🔍 Top source:")
            top_result = result['retrieval_results'][0]
            print(f"   Source: {top_result['source']} (page {top_result['page']})")
            print(f"   Score: {top_result['score']}")
        
        print("\n" + "."*50)
        time.sleep(1)  # Brief pause between questions

def demo_interactive_mode(chatbot):
    """Demonstrate interactive mode."""
    print_separator("💬 INTERACTIVE MODE DEMO")
    
    print("You can now ask questions interactively!")
    print("Type 'quit' to exit, 'help' for commands.")
    print("-" * 40)
    
    while True:
        try:
            question = input("\n🔹 Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif question.lower() == 'help':
                print("Available commands:")
                print("  help    - Show this help message")
                print("  stats   - Show system statistics")
                print("  sources - List available document sources")
                print("  quit    - Exit the session")
                continue
            elif question.lower() == 'stats':
                stats = chatbot.get_stats()
                print(f"📊 System Statistics:")
                print(f"   - Total documents: {stats['vector_store']['total_documents']}")
                print(f"   - Chunk size: {stats['config']['chunk_size']}")
                print(f"   - Retrieval k: {stats['config']['retrieval_k']}")
                continue
            elif question.lower() == 'sources':
                sources = chatbot.get_available_sources()
                print(f"📚 Available sources ({len(sources)}):")
                for source in sources:
                    print(f"   - {source}")
                continue
            elif not question:
                continue
            
            # Get answer
            result = chatbot.ask_question(question)
            
            print(f"\n🤖 Answer:")
            print(result['answer'])
            
            if result['citations']:
                print(f"\n📚 {', '.join(result['citations'])}")
            
            print(f"📊 Confidence: {result['confidence']:.2f} | ⏱️ Time: {result['total_time']:.2f}s")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main demo function."""
    print("🎯 DOCUMENT CHATBOT DEMO")
    print("This demo will showcase the key features of the document chatbot system.")
    
    # Step 1: Document ingestion
    chatbot = demo_document_ingestion()
    
    if not chatbot:
        print("❌ Demo failed - could not initialize chatbot or ingest documents")
        return
    
    # Step 2: Question answering examples
    demo_question_answering(chatbot)
    
    # Step 3: Interactive mode (optional)
    print_separator("🎮 INTERACTIVE MODE")
    user_input = input("Would you like to try interactive mode? (y/n): ").lower().strip()
    
    if user_input in ['y', 'yes']:
        demo_interactive_mode(chatbot)
    
    print_separator("🎉 DEMO COMPLETE")
    print("Thank you for trying the Document Chatbot!")
    print("To run the web interface, use: streamlit run streamlit_app.py")
    print("To use the CLI, use: python main.py --help")

if __name__ == "__main__":
    main()
