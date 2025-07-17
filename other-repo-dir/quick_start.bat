@echo off
echo 🤖 Document Chatbot - Quick Start
echo ================================

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ✅ Virtual environment activated

REM Check if data folder exists and has files
if not exist "data" (
    echo 📁 Creating data folder...
    mkdir data
    echo ⚠️  Please add your documents (PDF, TXT, MD, DOCX) to the 'data' folder
    echo    You can use the existing 'machine_learning_yearning_by_andrew_ng.pdf' if available
) else (
    echo 📁 Data folder exists
    dir /b data\*.* 2>nul && (
        echo 📄 Files found in data folder:
        dir /b data\*.*
    ) || (
        echo ⚠️  No files found in data folder. Please add documents.
    )
)

echo.
echo 🚀 Quick Commands:
echo   1. Test installation: python verify_installation.py
echo   2. Ingest documents:   python main.py ingest data --reset
echo   3. Ask a question:     python main.py ask "What is machine learning?"
echo   4. Interactive mode:   python main.py interactive
echo   5. Web interface:      streamlit run streamlit_app.py
echo   6. Get help:           python main.py --help
echo.

REM Keep window open
cmd /k
