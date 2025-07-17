@echo off
REM Document Chatbot Demo Script for Windows
REM This script demonstrates the key features of the document chatbot system

echo 🎯 Document Chatbot Demo Script
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 🏗️  Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt

REM Check if data folder exists
if not exist "data" (
    echo 📁 Creating data folder...
    mkdir data
    echo ⚠️  Please add your documents (PDF, TXT, MD, DOCX) to the 'data' folder
    echo    For testing, you can use the provided 'machine_learning_yearning_by_andrew_ng.pdf'
)

echo.
echo 🚀 Starting Demo...
echo.

REM Demo 1: CLI Document Ingestion
echo 1️⃣  CLI Document Ingestion Demo
echo ================================
echo Ingesting documents from data folder...
python main.py ingest data --reset

echo.
echo 2️⃣  CLI Question Answering Demo
echo ==============================

REM Example questions
echo.
echo Question: What is machine learning?
echo -----------------------------------
python main.py ask "What is machine learning?" --show-sources
echo.
timeout /t 2 /nobreak >nul

echo Question: What are the key principles of ML engineering?
echo --------------------------------------------------------
python main.py ask "What are the key principles of ML engineering?" --show-sources
echo.
timeout /t 2 /nobreak >nul

echo Question: How should I split my data?
echo ------------------------------------
python main.py ask "How should I split my data?" --show-sources
echo.
timeout /t 2 /nobreak >nul

echo.
echo 3️⃣  Interactive CLI Demo
echo =======================
echo Starting interactive CLI session...
echo Type 'help' for commands, 'quit' to exit
python main.py interactive

echo.
echo 4️⃣  Python Demo Script
echo =====================
echo Running Python demo script...
python demo.py

echo.
echo 5️⃣  Web Interface
echo ================
echo To start the web interface, run:
echo streamlit run streamlit_app.py
echo.
echo 🎉 Demo Complete!
echo ==================
echo Thank you for trying the Document Chatbot!
pause
