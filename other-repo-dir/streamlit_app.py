"""
Enhanced Streamlit web interface for the document chatbot.
"""

import streamlit as st
import logging
from pathlib import Path
import time
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.chatbot import DocumentChatbot
from app.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Document Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_initialized' not in st.session_state:
    st.session_state.is_initialized = False

def initialize_chatbot(model_path=None):
    """Initialize the chatbot."""
    try:
        config = get_config()
        st.session_state.chatbot = DocumentChatbot(config=config, model_path=model_path)
        st.session_state.is_initialized = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {e}")
        return False

def main():
    st.title("🤖 Document Chatbot")
    st.markdown("Ask questions about your documents and get answers with citations!")
    
    # Sidebar for configuration and stats
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model path input
        model_path = st.text_input(
            "LLM Model Path (optional)",
            help="Path to your local LLM model file (e.g., .gguf file)"
        )
        
        # Initialize chatbot button
        if st.button("🚀 Initialize Chatbot", type="primary"):
            with st.spinner("Initializing chatbot..."):
                if initialize_chatbot(model_path if model_path else None):
                    st.success("Chatbot initialized successfully!")
                else:
                    st.error("Failed to initialize chatbot")
        
        # Show stats if chatbot is initialized
        if st.session_state.is_initialized:
            st.header("📊 Statistics")
            try:
                stats = st.session_state.chatbot.get_stats()
                st.metric("Total Documents", stats['vector_store']['total_documents'])
                st.metric("Chunk Size", stats['config']['chunk_size'])
                st.metric("Retrieval K", stats['config']['retrieval_k'])
                
                # Available sources
                sources = st.session_state.chatbot.get_available_sources()
                if sources:
                    st.subheader("📚 Available Sources")
                    for source in sources[:10]:  # Show first 10
                        st.text(f"• {source}")
                    if len(sources) > 10:
                        st.text(f"... and {len(sources) - 10} more")
                        
            except Exception as e:
                st.error(f"Error getting stats: {e}")
        
        # Document management
        st.header("📁 Document Management")
        
        if st.button("🗑️ Reset Knowledge Base", type="secondary"):
            if st.session_state.is_initialized:
                with st.spinner("Resetting knowledge base..."):
                    result = st.session_state.chatbot.reset_knowledge_base()
                    if result['success']:
                        st.success("Knowledge base reset successfully!")
                        st.session_state.chat_history = []
                    else:
                        st.error(f"Error: {result['message']}")
            else:
                st.warning("Please initialize the chatbot first")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Document ingestion section
        st.header("📚 Document Ingestion")
        
        # Folder upload (simulated with text input since Streamlit doesn't support folder upload)
        folder_path = st.text_input(
            "Document Folder Path",
            placeholder="Enter the path to your documents folder",
            help="Path to folder containing PDF, TXT, MD, or DOCX files"
        )
        
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            reset_before_ingest = st.checkbox("Reset before ingestion", value=False)
        
        with col1_2:
            if st.button("📥 Ingest Documents", type="primary"):
                if not st.session_state.is_initialized:
                    st.error("Please initialize the chatbot first")
                elif not folder_path:
                    st.error("Please provide a folder path")
                elif not Path(folder_path).exists():
                    st.error("Folder path does not exist")
                else:
                    with st.spinner("Processing documents..."):
                        if reset_before_ingest:
                            st.session_state.chatbot.reset_knowledge_base()
                        
                        result = st.session_state.chatbot.ingest_documents(folder_path)
                        
                        if result['success']:
                            st.success(result['message'])
                            stats = result['stats']
                            st.info(f"Processing time: {stats.get('processing_time', 0):.2f}s")
                        else:
                            st.error(result['message'])
        
        # Chat interface
        st.header("💬 Chat Interface")
        
        # Display chat history
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            with st.container():
                st.markdown(f"**🙋 You:** {question}")
                st.markdown(f"**🤖 Bot:** {answer['answer']}")
                
                if answer.get('citations'):
                    st.caption(f"📚 Sources: {', '.join(answer['citations'])}")
                
                st.caption(f"⏱️ Response time: {answer.get('total_time', 0):.2f}s | 📊 Confidence: {answer.get('confidence', 0):.2f}")
                st.divider()
        
        # Question input
        question = st.text_input(
            "Ask a question:",
            placeholder="What would you like to know about your documents?",
            key="question_input"
        )
        
        col_ask1, col_ask2 = st.columns([1, 4])
        
        with col_ask1:
            k_value = st.number_input("Retrieve K docs", min_value=1, max_value=20, value=5)
        
        with col_ask2:
            if st.button("❓ Ask Question", type="primary") or (question and st.session_state.get('ask_on_enter', False)):
                if not st.session_state.is_initialized:
                    st.error("Please initialize the chatbot first")
                elif not question:
                    st.error("Please enter a question")
                else:
                    with st.spinner("Thinking..."):
                        start_time = time.time()
                        answer = st.session_state.chatbot.ask_question(question, k=k_value)
                        
                        # Add to chat history
                        st.session_state.chat_history.append((question, answer))
                        
                        # Clear the input
                        st.session_state.question_input = ""
                        st.rerun()
    
    with col2:
        st.header("🔍 Search Results")
        
        if st.session_state.chat_history:
            latest_answer = st.session_state.chat_history[-1][1]
            
            if latest_answer.get('retrieval_results'):
                st.subheader("📄 Retrieved Documents")
                
                for i, result in enumerate(latest_answer['retrieval_results'], 1):
                    with st.expander(f"{i}. {result['source']} (Score: {result['score']})"):
                        st.text(f"Page: {result['page']}")
                        st.text_area(
                            "Content:", 
                            result['content'], 
                            height=150, 
                            key=f"content_{i}_{len(st.session_state.chat_history)}"
                        )
        else:
            st.info("Ask a question to see search results here")
        
        # Performance metrics
        if st.session_state.chat_history:
            st.subheader("📈 Performance")
            latest_answer = st.session_state.chat_history[-1][1]
            
            col_perf1, col_perf2 = st.columns(2)
            with col_perf1:
                st.metric("Total Time", f"{latest_answer.get('total_time', 0):.2f}s")
            with col_perf2:
                st.metric("Confidence", f"{latest_answer.get('confidence', 0):.2f}")

if __name__ == "__main__":
    main()
