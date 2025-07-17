# 🤖 Document Chatbot - Advanced RAG System

A production-ready chatbot system that answers questions from uploaded document collections using Retrieval-Augmented Generation (RAG). The system extracts relevant passages, generates grounded answers, and provides proper citations with page references.

## 🎯 Features

### Core Functionality
- **Document Ingestion**: Support for PDF, TXT, MD, and DOCX files
- **Intelligent Retrieval**: Vector-based similarity search with confidence scoring
- **Grounded Generation**: Answers based only on provided documents
- **Citation System**: Inline citations with page/line references `[DocName, page X]`
- **Answer Refusal**: Says "I don't know" when information isn't available
- **Performance Optimized**: End-to-end latency ≤ 3 seconds per query

### Interfaces
- **CLI Tool**: Command-line interface for document ingestion and querying
- **Web UI**: Modern Streamlit interface with real-time chat
- **Python API**: Programmatic access for integration
- **Demo Scripts**: Ready-to-run examples and tutorials

### Technical Features
- **Modular Architecture**: Clean separation of concerns with `app/` package
- **Vector Storage**: ChromaDB for persistent embeddings
- **Flexible Models**: Support for local LLMs (Llama 2) and embedding models
- **Chunk Management**: Intelligent text chunking with overlap
- **Confidence Thresholds**: Configurable relevance scoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Documents     │    │   Text Chunks    │    │   Embeddings    │
│                 │───▶│                  │───▶│                 │
│ • PDF, TXT, MD  │    │ • Smart chunking │    │ • Vector Store  │
│ • DOCX files    │    │ • Metadata       │    │ • ChromaDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│   User Query    │───▶│   Retrieval      │◄────────────┘
└─────────────────┘    │                  │
                       │ • Similarity     │
                       │ • Top-k chunks   │
                       │ • Confidence     │
                       └──────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Final Answer  │◄───│   Generation     │◄───│   Context       │
│                 │    │                  │    │                 │
│ • Grounded text │    │ • LLM (Llama 2)  │    │ • Retrieved     │
│ • Citations     │    │ • Answer refusal │    │ • Formatted     │
│ • Confidence    │    │ • Length limit   │    │ • With metadata │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd document-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Document Ingestion

```bash
# Ingest documents from a folder (CLI)
python main.py ingest data/ --reset

# Or use the Python API
python demo.py
```

### 3. Ask Questions

```bash
# CLI interface
python main.py ask "What is machine learning?"

# Interactive mode
python main.py interactive

# Web interface
streamlit run streamlit_app.py
```

## 📦 Project Structure

```
document-chatbot/
├── app/                          # Core package
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration settings
│   ├── document_processor.py    # Document parsing and chunking
│   ├── vector_store.py          # ChromaDB vector operations
│   ├── retriever.py             # Document retrieval logic
│   ├── generator.py             # Answer generation with LLM
│   └── chatbot.py               # Main orchestration class
├── data/                        # Document storage
├── chroma_db/                   # Vector database
├── main.py                      # CLI entry point
├── streamlit_app.py            # Web interface
├── demo.py                     # Python demo script
├── demo.sh / demo.bat          # Shell demo scripts
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## 🎮 Usage Examples

### CLI Commands

```bash
# Document ingestion
python main.py ingest /path/to/documents --reset
python main.py ingest /path/to/documents --model-path /path/to/llama-model.gguf

# Question answering
python main.py ask "What is the main topic?" --k 5 --show-sources
python main.py ask "Explain the methodology" --model-path /path/to/model.gguf

# Interactive session
python main.py interactive

# System statistics
python main.py stats

# Reset knowledge base
python main.py reset --confirm
```

### Python API

```python
from app.chatbot import DocumentChatbot

# Initialize chatbot
chatbot = DocumentChatbot()

# Ingest documents
result = chatbot.ingest_documents("data/")
print(f"Processed {result['stats']['new_chunks']} chunks")

# Ask questions
answer = chatbot.ask_question("What is machine learning?")
print(f"Answer: {answer['answer']}")
print(f"Citations: {answer['citations']}")
print(f"Confidence: {answer['confidence']:.2f}")
```

### Web Interface Features

- **Document Upload**: Easy folder path input for ingestion
- **Real-time Chat**: Interactive conversation with chat history
- **Source Display**: View retrieved document chunks and scores
- **Performance Metrics**: Response time and confidence tracking
- **Knowledge Management**: Reset and statistics viewing

## ⚙️ Configuration

### Key Settings

```python
# Embedding configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"  # or "cuda"

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval settings
RETRIEVAL_K = 5
CONFIDENCE_THRESHOLD = 0.3

# Generation limits
MAX_TOKENS = 500
TEMPERATURE = 0.1
```

### LLM Model Setup

1. **Download a model** (e.g., from Hugging Face):
   ```bash
   # Example: Llama 2 7B Chat GGUF
   wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf
   ```

2. **Use with the system**:
   ```bash
   python main.py ask "Your question" --model-path ./llama-2-7b-chat.Q4_K_M.gguf
   ```

## 🔧 Advanced Configuration

### Custom Configuration

Edit `app/config.py` to customize:

- **Vector store settings**: Chunk size, overlap, collection name
- **Retrieval parameters**: Number of results, confidence thresholds
- **LLM settings**: Model parameters, token limits, temperature
- **Citation format**: Page numbering, citation style
- **Performance tuning**: Batch sizes, caching options

### Environment Variables

```bash
# Optional environment variables
export CHATBOT_MODEL_PATH="/path/to/your/model.gguf"
export CHATBOT_CHUNK_SIZE=1000
export CHATBOT_CONFIDENCE_THRESHOLD=0.3
```

## 🎯 Demo Scripts

### Quick Demo

```bash
# Windows
demo.bat

# macOS/Linux
./demo.sh

# Python
python demo.py
```

The demo includes:
1. Document ingestion from `data/` folder
2. Example question answering
3. Interactive CLI session
4. Performance benchmarking

### Example Questions

- "What is machine learning?"
- "What are the key principles mentioned in the document?"
- "Can you summarize the main topics covered?"
- "How should I approach model evaluation?"

## 📊 Performance & Optimization

### Latency Optimization

- **Chunk Size**: Smaller chunks = faster retrieval, larger chunks = better context
- **Retrieval K**: Fewer results = faster processing, more results = better coverage
- **Model Choice**: Smaller models = faster inference, larger models = better quality
- **GPU Acceleration**: Enable for significantly faster LLM inference

### Confidence Tuning

- **High Threshold (0.5+)**: Conservative answers, fewer false positives
- **Medium Threshold (0.3-0.5)**: Balanced approach
- **Low Threshold (0.1-0.3)**: More permissive, may include marginal results

### Scaling Considerations

- **Large Document Collections**: Consider chunking strategies and indexing
- **High Query Volume**: Implement caching and batch processing
- **Multi-User**: Add session management and resource allocation

## 🐛 Troubleshooting

### Common Issues

1. **"No documents found"**
   - Check file formats (PDF, TXT, MD, DOCX supported)
   - Verify folder path exists and contains documents
   - Check file permissions

2. **Poor answer quality**
   - Adjust confidence threshold
   - Increase retrieval K value
   - Verify document content quality
   - Consider different embedding model

3. **Slow performance**
   - Enable GPU acceleration
   - Reduce chunk size or retrieval K
   - Use smaller LLM model
   - Check system resources

4. **"I don't know" responses**
   - Lower confidence threshold
   - Check if question relates to document content
   - Verify documents were ingested successfully

### Debug Mode

```bash
# Enable verbose logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from app.chatbot import DocumentChatbot
chatbot = DocumentChatbot()
result = chatbot.ask_question('test question')
print(result)
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

## 🙏 Acknowledgments

- **LangChain**: Framework for LLM applications
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Embedding models
- **Streamlit**: Web interface framework
- **Llama 2**: Large language model by Meta

**Happy chatting with your documents! 🎉**

