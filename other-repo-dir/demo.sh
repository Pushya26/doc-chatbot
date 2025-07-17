#!/bin/bash

# Document Chatbot Demo Script
# This script demonstrates the key features of the document chatbot system

echo "🎯 Document Chatbot Demo Script"
echo "==============================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🏗️  Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Check if data folder exists
if [ ! -d "data" ]; then
    echo "📁 Creating data folder..."
    mkdir data
    echo "⚠️  Please add your documents (PDF, TXT, MD, DOCX) to the 'data' folder"
    echo "   For testing, you can use the provided 'machine_learning_yearning_by_andrew_ng.pdf'"
fi

echo ""
echo "🚀 Starting Demo..."
echo ""

# Demo 1: CLI Document Ingestion
echo "1️⃣  CLI Document Ingestion Demo"
echo "================================"
echo "Ingesting documents from data folder..."
python main.py ingest data --reset

echo ""
echo "2️⃣  CLI Question Answering Demo"
echo "==============================="

# Example questions
questions=(
    "What is machine learning?"
    "What are the key principles of ML engineering?"
    "How should I split my data?"
)

for question in "${questions[@]}"; do
    echo ""
    echo "Question: $question"
    echo "-------------------"
    python main.py ask "$question" --show-sources
    echo ""
    sleep 2
done

echo ""
echo "3️⃣  Interactive CLI Demo"
echo "======================="
echo "Starting interactive CLI session..."
echo "Type 'help' for commands, 'quit' to exit"
python main.py interactive

echo ""
echo "4️⃣  Python Demo Script"
echo "====================="
echo "Running Python demo script..."
python demo.py

echo ""
echo "5️⃣  Web Interface"
echo "================"
echo "To start the web interface, run:"
echo "streamlit run streamlit_app.py"
echo ""
echo "🎉 Demo Complete!"
echo "=================="
echo "Thank you for trying the Document Chatbot!"
