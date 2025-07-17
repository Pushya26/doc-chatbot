"""
Command-line interface for document ingestion and querying.
"""

import click
import logging
from pathlib import Path
import sys
import os

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.chatbot import DocumentChatbot
from app.config import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
@click.option('--config-file', help='Path to configuration file')
@click.pass_context
def cli(ctx, config_file):
    """Document Chatbot CLI - A system for answering questions from document collections."""
    ctx.ensure_object(dict)
    
    # Load configuration
    config = get_config()
    if config_file and Path(config_file).exists():
        # TODO: Load custom config file
        pass
    
    ctx.obj['config'] = config

@cli.command()
@click.argument('folder_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--model-path', help='Path to LLM model file (optional)')
@click.option('--reset', is_flag=True, help='Reset existing knowledge base before ingestion')
@click.pass_context
def ingest(ctx, folder_path, model_path, reset):
    """Ingest documents from a folder into the knowledge base."""
    config = ctx.obj['config']
    
    click.echo(f"🔍 Initializing chatbot...")
    chatbot = DocumentChatbot(config=config, model_path=model_path)
    
    if reset:
        click.echo("🗑️  Resetting knowledge base...")
        result = chatbot.reset_knowledge_base()
        if result['success']:
            click.echo("✅ Knowledge base reset successfully")
        else:
            click.echo(f"❌ Error resetting knowledge base: {result['message']}")
            return
    
    click.echo(f"📚 Ingesting documents from: {folder_path}")
    
    result = chatbot.ingest_documents(folder_path)
    
    if result['success']:
        stats = result['stats']
        click.echo(f"✅ {result['message']}")
        click.echo(f"📊 Statistics:")
        click.echo(f"   - New chunks: {stats.get('new_chunks', 0)}")
        click.echo(f"   - Total documents: {stats.get('total_documents', 0)}")
        click.echo(f"   - Processing time: {stats.get('processing_time', 0):.2f}s")
    else:
        click.echo(f"❌ {result['message']}")

@cli.command()
@click.argument('question')
@click.option('--model-path', help='Path to LLM model file (optional)')
@click.option('--k', default=5, help='Number of documents to retrieve')
@click.option('--show-sources', is_flag=True, help='Show source documents')
@click.pass_context
def ask(ctx, question, model_path, k, show_sources):
    """Ask a question to the chatbot."""
    config = ctx.obj['config']
    
    click.echo(f"🤖 Initializing chatbot...")
    chatbot = DocumentChatbot(config=config, model_path=model_path)
    
    click.echo(f"❓ Question: {question}")
    click.echo("🔍 Searching for relevant information...")
    
    result = chatbot.ask_question(question, k=k)
    
    click.echo("\n" + "="*60)
    click.echo("📝 ANSWER:")
    click.echo("="*60)
    click.echo(result['answer'])
    
    if result['citations']:
        click.echo(f"\n📚 Citations: {', '.join(result['citations'])}")
    
    click.echo(f"\n📊 Confidence: {result['confidence']:.2f}")
    click.echo(f"⏱️  Response time: {result['total_time']:.2f}s")
    
    if show_sources and result['retrieval_results']:
        click.echo(f"\n🔍 Source Documents:")
        click.echo("-" * 40)
        for i, source in enumerate(result['retrieval_results'], 1):
            click.echo(f"{i}. {source['source']} (page {source['page']}) - Score: {source['score']}")
            click.echo(f"   Content: {source['content']}")
            click.echo()

@cli.command()
@click.option('--model-path', help='Path to LLM model file (optional)')
@click.pass_context
def interactive(ctx, model_path):
    """Start an interactive chat session."""
    config = ctx.obj['config']
    
    click.echo("🤖 Initializing chatbot...")
    chatbot = DocumentChatbot(config=config, model_path=model_path)
    
    # Check if we have any documents
    stats = chatbot.get_stats()
    if stats['vector_store']['total_documents'] == 0:
        click.echo("⚠️  No documents found in knowledge base. Please ingest documents first using 'python main.py ingest <folder_path>'")
        return
    
    click.echo(f"📚 Loaded {stats['vector_store']['total_documents']} document chunks")
    click.echo("💬 Starting interactive session. Type 'quit' to exit, 'help' for commands.")
    click.echo("-" * 60)
    
    while True:
        try:
            question = click.prompt("\n🔹 Your question", type=str).strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                click.echo("👋 Goodbye!")
                break
            elif question.lower() == 'help':
                click.echo("Available commands:")
                click.echo("  help    - Show this help message")
                click.echo("  stats   - Show system statistics")
                click.echo("  sources - List available document sources")
                click.echo("  quit    - Exit the session")
                continue
            elif question.lower() == 'stats':
                stats = chatbot.get_stats()
                click.echo(f"📊 System Statistics:")
                click.echo(f"   - Total documents: {stats['vector_store']['total_documents']}")
                click.echo(f"   - Chunk size: {stats['config']['chunk_size']}")
                click.echo(f"   - Retrieval k: {stats['config']['retrieval_k']}")
                continue
            elif question.lower() == 'sources':
                sources = chatbot.get_available_sources()
                click.echo(f"📚 Available sources ({len(sources)}):")
                for source in sources:
                    click.echo(f"   - {source}")
                continue
            elif not question:
                continue
            
            # Get answer
            result = chatbot.ask_question(question)
            
            click.echo(f"\n🤖 Answer:")
            click.echo(result['answer'])
            
            if result['citations']:
                click.echo(f"\n📚 {', '.join(result['citations'])}")
            
            click.echo(f"📊 Confidence: {result['confidence']:.2f} | ⏱️ Time: {result['total_time']:.2f}s")
            
        except KeyboardInterrupt:
            click.echo("\n👋 Goodbye!")
            break
        except Exception as e:
            click.echo(f"❌ Error: {e}")

@cli.command()
@click.option('--model-path', help='Path to LLM model file (optional)')
@click.pass_context
def stats(ctx, model_path):
    """Show system statistics."""
    config = ctx.obj['config']
    
    chatbot = DocumentChatbot(config=config, model_path=model_path)
    stats = chatbot.get_stats()
    
    click.echo("📊 System Statistics:")
    click.echo("=" * 40)
    click.echo(f"Total documents: {stats['vector_store']['total_documents']}")
    click.echo(f"Collection name: {stats['vector_store']['collection_name']}")
    click.echo(f"Persist directory: {stats['vector_store']['persist_directory']}")
    click.echo(f"Chunk size: {stats['config']['chunk_size']}")
    click.echo(f"Chunk overlap: {stats['config']['chunk_overlap']}")
    click.echo(f"Retrieval k: {stats['config']['retrieval_k']}")
    click.echo(f"Confidence threshold: {stats['config']['confidence_threshold']}")

@cli.command()
@click.option('--model-path', help='Path to LLM model file (optional)')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset(ctx, model_path, confirm):
    """Reset the knowledge base (delete all documents)."""
    config = ctx.obj['config']
    
    if not confirm:
        if not click.confirm("⚠️  This will delete all documents from the knowledge base. Continue?"):
            click.echo("Operation cancelled.")
            return
    
    chatbot = DocumentChatbot(config=config, model_path=model_path)
    result = chatbot.reset_knowledge_base()
    
    if result['success']:
        click.echo("✅ Knowledge base reset successfully")
    else:
        click.echo(f"❌ {result['message']}")

if __name__ == '__main__':
    cli()
