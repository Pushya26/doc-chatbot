"""
Quick test to identify missing packages
"""

def test_missing_packages():
    missing = []
    
    packages_to_test = [
        'PyPDF2',
        'pdfplumber', 
        'docx',
        'markdown',
        'streamlit',
        'langchain',
        'langchain_community',
        'chromadb',
        'sentence_transformers',
        'numpy',
        'pandas',
        'click',
        'fastapi',
        'uvicorn'
    ]
    
    for package in packages_to_test:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n🔧 To install missing packages:")
        print(f"venv\\Scripts\\pip install {' '.join(missing)}")
    else:
        print(f"\n🎉 All packages are installed!")

if __name__ == "__main__":
    test_missing_packages()
