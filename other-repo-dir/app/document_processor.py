"""
Document processing module for handling various file formats.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Try importing PDF libraries with fallbacks
try:
    import PyPDF2
except ImportError:
    try:
        import pypdf as PyPDF2
    except ImportError:
        raise ImportError("Neither PyPDF2 nor pypdf could be imported. Please install one of them.")

import pdfplumber
from docx import Document
import markdown

from .config import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document."""
    content: str
    metadata: Dict[str, Any]
    source: str
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    chunk_id: Optional[str] = None

class DocumentProcessor:
    """Processes documents and extracts text content with metadata."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_folder(self, folder_path: str) -> List[DocumentChunk]:
        """Process all supported documents in a folder."""
        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        chunks = []
        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                try:
                    file_chunks = self.process_file(str(file_path))
                    chunks.extend(file_chunks)
                    logger.info(f"Processed {file_path.name}: {len(file_chunks)} chunks")
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        return chunks
    
    def process_file(self, file_path: str) -> List[DocumentChunk]:
        """Process a single file and return chunks."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        if extension not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")
        
        # Extract text based on file type
        if extension == ".pdf":
            text_content = self._extract_pdf_text(file_path)
        elif extension == ".txt":
            text_content = self._extract_text_file(file_path)
        elif extension == ".md":
            text_content = self._extract_markdown_file(file_path)
        elif extension == ".docx":
            text_content = self._extract_docx_file(file_path)
        else:
            raise ValueError(f"Handler not implemented for {extension}")
        
        # Create chunks
        chunks = self._create_chunks(text_content, str(file_path))
        return chunks
    
    def _extract_pdf_text(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page information."""
        pages_content = []
        
        try:
            # Use pdfplumber for better text extraction
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_content.append({
                            "text": text,
                            "page": page_num,
                            "source": str(file_path)
                        })
        except Exception as e:
            logger.warning(f"pdfplumber failed for {file_path}, trying PyPDF2: {e}")
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        if text:
                            pages_content.append({
                                "text": text,
                                "page": page_num,
                                "source": str(file_path)
                            })
            except Exception as e2:
                logger.error(f"Both PDF extractors failed for {file_path}: {e2}")
                raise
        
        return pages_content
    
    def _extract_text_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return [{
                    "text": content,
                    "page": 1,
                    "source": str(file_path)
                }]
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                return [{
                    "text": content,
                    "page": 1,
                    "source": str(file_path)
                }]
    
    def _extract_markdown_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from markdown file."""
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
            # Convert markdown to plain text
            html = markdown.markdown(md_content)
            # Simple HTML tag removal (could use BeautifulSoup for better handling)
            import re
            text = re.sub(r'<[^>]+>', '', html)
            
            return [{
                "text": text,
                "page": 1,
                "source": str(file_path)
            }]
    
    def _extract_docx_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from Word document."""
        doc = Document(file_path)
        paragraphs = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        
        content = "\n".join(paragraphs)
        return [{
            "text": content,
            "page": 1,
            "source": str(file_path)
        }]
    
    def _create_chunks(self, pages_content: List[Dict[str, Any]], source: str) -> List[DocumentChunk]:
        """Create text chunks from extracted content."""
        chunks = []
        
        for page_content in pages_content:
            text = page_content["text"]
            page_num = page_content["page"]
            
            # Split text into chunks
            words = text.split()
            
            for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
                chunk_words = words[i:i + self.chunk_size]
                chunk_text = " ".join(chunk_words)
                
                if len(chunk_text.strip()) > 50:  # Skip very small chunks
                    chunk = DocumentChunk(
                        content=chunk_text,
                        source=source,
                        page_number=page_num,
                        metadata={
                            "file_name": Path(source).name,
                            "file_path": source,
                            "page": page_num,
                            "chunk_size": len(chunk_text),
                            "word_count": len(chunk_words)
                        },
                        chunk_id=f"{Path(source).stem}_page_{page_num}_chunk_{len(chunks)}"
                    )
                    chunks.append(chunk)
        
        return chunks
