# Enhanced Streamlit app using the new chatbot system
# This provides backward compatibility with the original app.py

import streamlit as st
import logging
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.chatbot import DocumentChatbot
    from app.config import get_config
    NEW_SYSTEM_AVAILABLE = True
except ImportError:
    # Fallback to original system if new system is not available
    NEW_SYSTEM_AVAILABLE = False
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.llms import LlamaCpp
    from langchain.callbacks.manager import CallbackManager
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    from langchain.chains.question_answering import load_qa_chain

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set web page title and icon
st.set_page_config(
    page_title="Chat with PDF",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False

def initialize_new_system():
    """Initialize the new enhanced system."""
    try:
        config = get_config()
        st.session_state.chatbot = DocumentChatbot(config=config)
        st.session_state.system_initialized = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize new system: {e}")
        return False

def initialize_legacy_system():
    """Initialize the legacy system (original app.py logic)."""
    try:
        # Define embedding model
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        
        # Initialize Chroma vector store
        db = Chroma(persist_directory="./chroma_db/", embedding_function=embeddings)
        
        # Check if we can initialize LLM (optional)
        llm = None
        model_path = os.getenv("LLM_MODEL_PATH")
        if model_path and Path(model_path).exists():
            try:
                callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
                llm = LlamaCpp(
                    model_path=model_path,
                    max_tokens=256,
                    n_gpu_layers=0,
                    n_batch=512,
                    callback_manager=callback_manager,
                    n_ctx=2048,
                    verbose=False,
                )
            except Exception as e:
                st.warning(f"Could not load LLM model: {e}")
        
        st.session_state.db = db
        st.session_state.llm = llm
        st.session_state.embeddings = embeddings
        st.session_state.system_initialized = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize legacy system: {e}")
        return False

def main():
    # Header
    if NEW_SYSTEM_AVAILABLE:
        st.title('🤖 Enhanced Document Chatbot')
        st.markdown("""
        This is an enhanced version of the document chatbot with improved features:
        - Multiple file format support (PDF, TXT, MD, DOCX)
        - Better citation system with page references
        - Confidence scoring and answer refusal
        - Improved performance and modularity
        """)
    else:
        st.title('💬 Chat with PDF 📄 (Powered by Llama 2 🦙🦙)')
        st.markdown("""
        This is the demonstration of a chatbot with PDF with Llama 2, Chroma, and Streamlit.
        I read the book Machine Learning Yearning by Andrew Ng. Please ask me any questions about this book.
        """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System selection
        if NEW_SYSTEM_AVAILABLE:
            system_type = st.selectbox(
                "System Type",
                ["Enhanced System", "Legacy System"],
                help="Choose which system to use"
            )
            use_new_system = (system_type == "Enhanced System")
        else:
            use_new_system = False
            st.info("Enhanced system not available. Using legacy system.")
        
        # Model configuration
        model_path = st.text_input(
            "LLM Model Path (optional)",
            help="Path to your local LLM model file"
        )
        
        if model_path:
            os.environ["LLM_MODEL_PATH"] = model_path
        
        # Initialize system button
        if st.button("🚀 Initialize System", type="primary"):
            with st.spinner("Initializing system..."):
                if use_new_system and NEW_SYSTEM_AVAILABLE:
                    success = initialize_new_system()
                else:
                    success = initialize_legacy_system()
                
                if success:
                    st.success("System initialized successfully!")
                else:
                    st.error("Failed to initialize system")
        
        # System statistics
        if st.session_state.system_initialized:
            st.header("📊 Statistics")
            
            if use_new_system and NEW_SYSTEM_AVAILABLE:
                try:
                    stats = st.session_state.chatbot.get_stats()
                    st.metric("Total Documents", stats['vector_store']['total_documents'])
                    st.metric("Chunk Size", stats['config']['chunk_size'])
                    
                    # Show available sources
                    sources = st.session_state.chatbot.get_available_sources()
                    if sources:
                        st.subheader("📚 Available Sources")
                        for source in sources[:5]:
                            st.text(f"• {source}")
                        if len(sources) > 5:
                            st.text(f"... and {len(sources) - 5} more")
                except Exception as e:
                    st.error(f"Error getting stats: {e}")
            else:
                st.text("Legacy system - limited stats available")

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Document ingestion section (new system only)
        if use_new_system and NEW_SYSTEM_AVAILABLE:
            st.header("📚 Document Ingestion")
            
            folder_path = st.text_input(
                "Document Folder Path",
                placeholder="Enter path to your documents folder",
                help="Folder containing PDF, TXT, MD, or DOCX files"
            )
            
            col1_1, col1_2 = st.columns(2)
            with col1_1:
                reset_before_ingest = st.checkbox("Reset before ingestion", value=False)
            
            with col1_2:
                if st.button("📥 Ingest Documents", type="primary"):
                    if not st.session_state.system_initialized:
                        st.error("Please initialize the system first")
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
                
                if isinstance(answer, dict):
                    # New system response
                    st.markdown(f"**🤖 Bot:** {answer['answer']}")
                    if answer.get('citations'):
                        st.caption(f"📚 Sources: {', '.join(answer['citations'])}")
                    st.caption(f"⏱️ {answer.get('total_time', 0):.2f}s | 📊 Confidence: {answer.get('confidence', 0):.2f}")
                else:
                    # Legacy system response
                    st.markdown(f"**🤖 Bot:** {answer}")
                
                st.divider()
        
        # Question input
        question = st.text_input(
            "Ask a question:",
            placeholder="What would you like to know about your documents?",
            key="question_input"
        )
        
        # Ask question button
        if st.button("❓ Ask Question", type="primary") or (question and st.session_state.get('submit_on_enter')):
            if not st.session_state.system_initialized:
                st.error("Please initialize the system first")
            elif not question:
                st.error("Please enter a question")
            else:
                with st.spinner("Thinking..."):
                    if use_new_system and NEW_SYSTEM_AVAILABLE:
                        # Use new system
                        answer = st.session_state.chatbot.ask_question(question)
                        st.session_state.chat_history.append((question, answer))
                    else:
                        # Use legacy system
                        try:
                            docs = st.session_state.db.similarity_search(question)
                            
                            if st.session_state.llm:
                                chain = load_qa_chain(st.session_state.llm, chain_type="stuff")
                                response = chain.run(input_documents=docs, question=question)
                            else:
                                # Simple fallback without LLM
                                response = f"Based on the documents, here are the most relevant passages:\n\n"
                                for i, doc in enumerate(docs[:2], 1):
                                    response += f"{i}. {doc.page_content[:200]}...\n\n"
                            
                            st.session_state.chat_history.append((question, response))
                        except Exception as e:
                            st.error(f"Error processing question: {e}")
                
                # Clear input and refresh
                st.session_state.question_input = ""
                st.rerun()
    
    with col2:
        st.header("🔍 Search Results")
        
        if st.session_state.chat_history:
            latest_answer = st.session_state.chat_history[-1][1]
            
            if isinstance(latest_answer, dict) and latest_answer.get('retrieval_results'):
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
                st.info("Search results will appear here when using the enhanced system")
        else:
            st.info("Ask a question to see search results here")

if __name__ == "__main__":
    main()
