"""
FastAPI web interface for the document chatbot.
Alternative to Streamlit with REST API endpoints.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from pathlib import Path
import sys
import tempfile
import os
from typing import List, Optional

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.chatbot import DocumentChatbot
from app.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Chatbot API",
    description="A REST API for document-based question answering with citations",
    version="1.0.0"
)

# Global chatbot instance
chatbot = None

# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str
    k: Optional[int] = 5

class IngestionRequest(BaseModel):
    folder_path: str
    reset: Optional[bool] = False

class QuestionResponse(BaseModel):
    answer: str
    confidence: float
    citations: List[str]
    sources: List[str]
    total_time: float

class IngestionResponse(BaseModel):
    success: bool
    message: str
    stats: dict

# Initialize chatbot
@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup."""
    global chatbot
    try:
        config = get_config()
        chatbot = DocumentChatbot(config=config)
        logger.info("Chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "chatbot_ready": chatbot is not None}

# Document ingestion endpoint
@app.post("/ingest", response_model=IngestionResponse)
async def ingest_documents(request: IngestionRequest):
    """Ingest documents from a folder."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    if not Path(request.folder_path).exists():
        raise HTTPException(status_code=400, detail="Folder path does not exist")
    
    try:
        if request.reset:
            reset_result = chatbot.reset_knowledge_base()
            if not reset_result['success']:
                raise HTTPException(status_code=500, detail=reset_result['message'])
        
        result = chatbot.ingest_documents(request.folder_path)
        return IngestionResponse(**result)
    
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Question answering endpoint
@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question to the chatbot."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = chatbot.ask_question(request.question, k=request.k)
        
        return QuestionResponse(
            answer=result['answer'],
            confidence=result['confidence'],
            citations=result['citations'],
            sources=result['sources'],
            total_time=result['total_time']
        )
    
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search documents endpoint
@app.get("/search")
async def search_documents(query: str, k: int = 10):
    """Search documents without generating an answer."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        results = chatbot.search_documents(query, k=k)
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Statistics endpoint
@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        stats = chatbot.get_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Available sources endpoint
@app.get("/sources")
async def get_sources():
    """Get available document sources."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        sources = chatbot.get_available_sources()
        return {"sources": sources}
    
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Reset knowledge base endpoint
@app.post("/reset")
async def reset_knowledge_base():
    """Reset the knowledge base."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        result = chatbot.reset_knowledge_base()
        return result
    
    except Exception as e:
        logger.error(f"Error resetting knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File upload endpoint (alternative to folder path)
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), reset: bool = Form(False)):
    """Upload files directly to the system."""
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Save uploaded files
        for file in files:
            file_path = Path(temp_dir) / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        # Ingest documents
        if reset:
            reset_result = chatbot.reset_knowledge_base()
            if not reset_result['success']:
                raise HTTPException(status_code=500, detail=reset_result['message'])
        
        result = chatbot.ingest_documents(temp_dir)
        return IngestionResponse(**result)
    
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

# Simple HTML interface
@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve a simple HTML interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, button { padding: 10px; margin: 5px 0; }
            input[type="text"], textarea { width: 100%; }
            button { background: #007cba; color: white; border: none; cursor: pointer; }
            button:hover { background: #005a8a; }
            .response { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .error { background: #ffe6e6; color: #cc0000; }
            .success { background: #e6ffe6; color: #006600; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Document Chatbot</h1>
            <p>A REST API for document-based question answering with citations</p>
            
            <div class="form-group">
                <h2>📚 Ingest Documents</h2>
                <label for="folderPath">Folder Path:</label>
                <input type="text" id="folderPath" placeholder="Enter folder path containing documents">
                <label>
                    <input type="checkbox" id="resetBefore"> Reset knowledge base before ingestion
                </label>
                <button onclick="ingestDocuments()">Ingest Documents</button>
            </div>
            
            <div class="form-group">
                <h2>❓ Ask Question</h2>
                <label for="question">Question:</label>
                <textarea id="question" rows="3" placeholder="What would you like to know about your documents?"></textarea>
                <label for="kValue">Number of documents to retrieve (K):</label>
                <input type="number" id="kValue" value="5" min="1" max="20">
                <button onclick="askQuestion()">Ask Question</button>
            </div>
            
            <div class="form-group">
                <h2>📊 System Actions</h2>
                <button onclick="getStats()">Get Statistics</button>
                <button onclick="getSources()">Get Sources</button>
                <button onclick="resetKnowledgeBase()">Reset Knowledge Base</button>
            </div>
            
            <div id="response"></div>
        </div>
        
        <script>
            async function apiCall(url, method = 'GET', data = null) {
                const options = {
                    method: method,
                    headers: {'Content-Type': 'application/json'}
                };
                if (data) options.body = JSON.stringify(data);
                
                try {
                    const response = await fetch(url, options);
                    return await response.json();
                } catch (error) {
                    return {error: error.message};
                }
            }
            
            function showResponse(data, isError = false) {
                const responseDiv = document.getElementById('response');
                const className = isError ? 'response error' : 'response success';
                responseDiv.innerHTML = `<div class="${className}"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
            }
            
            async function ingestDocuments() {
                const folderPath = document.getElementById('folderPath').value;
                const reset = document.getElementById('resetBefore').checked;
                
                if (!folderPath) {
                    showResponse({error: 'Please enter a folder path'}, true);
                    return;
                }
                
                const data = await apiCall('/ingest', 'POST', {folder_path: folderPath, reset: reset});
                showResponse(data, data.error);
            }
            
            async function askQuestion() {
                const question = document.getElementById('question').value;
                const k = parseInt(document.getElementById('kValue').value);
                
                if (!question) {
                    showResponse({error: 'Please enter a question'}, true);
                    return;
                }
                
                const data = await apiCall('/ask', 'POST', {question: question, k: k});
                showResponse(data, data.error);
            }
            
            async function getStats() {
                const data = await apiCall('/stats');
                showResponse(data, data.error);
            }
            
            async function getSources() {
                const data = await apiCall('/sources');
                showResponse(data, data.error);
            }
            
            async function resetKnowledgeBase() {
                if (confirm('Are you sure you want to reset the knowledge base?')) {
                    const data = await apiCall('/reset', 'POST');
                    showResponse(data, data.error);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
