@echo off
echo 🛠️  Windows Installation Script for Document Chatbot
echo ===================================================

REM Check Python version
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies one by one to avoid conflicts
echo 📦 Installing core dependencies...
pip install numpy>=1.24.0
pip install pandas>=2.0.0
pip install python-dotenv>=1.0.0
pip install tqdm>=4.65.0
pip install click>=8.1.0

echo 📦 Installing document processing libraries...
pip install pypdf2>=3.0.0
pip install pdfplumber>=0.9.0
pip install python-docx>=0.8.11
pip install markdown>=3.4.0

echo 📦 Installing web frameworks...
pip install streamlit>=1.28.0
pip install fastapi>=0.100.0
pip install "uvicorn[standard]>=0.23.0"

echo 📦 Installing AI/ML libraries...
pip install sentence-transformers>=2.2.0
pip install huggingface-hub>=0.16.0
pip install chromadb>=0.4.0

echo 📦 Installing LangChain...
pip install langchain>=0.1.0
pip install langchain-community>=0.0.20
pip install langchain-core>=0.1.0

REM Create data folder
if not exist "data" (
    echo 📁 Creating data folder...
    mkdir data
)

REM Copy ML PDF if it exists
if exist "machine_learning_yearning_by_andrew_ng.pdf" (
    if not exist "data\machine_learning_yearning_by_andrew_ng.pdf" (
        copy "machine_learning_yearning_by_andrew_ng.pdf" "data\"
        echo ✅ Copied ML Yearning PDF to data folder
    )
)

echo.
echo 🧪 Testing installation...
python verify_installation.py

if errorlevel 1 (
    echo ❌ Installation test failed
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 🚀 Next steps:
echo   1. Add documents to the 'data' folder
echo   2. Run: python main.py ingest data --reset
echo   3. Run: python main.py ask "Your question here"
echo   4. Or use: streamlit run streamlit_app.py
echo.
echo To get started quickly, run: quick_start.bat
echo.
pause
