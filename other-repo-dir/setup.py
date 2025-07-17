"""
Setup script for the Document Chatbot system.
Helps users install dependencies and verify the installation.
"""

import subprocess
import sys
import os
from pathlib import Path
import platform

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title} ".center(60, "="))
    print("="*60)

def print_step(step_num, description):
    """Print a step description."""
    print(f"\n{step_num}. {description}")
    print("-" * 40)

def run_command(command, description, critical=True):
    """Run a command and handle errors."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        if critical:
            print("This is a critical step. Please fix the error and try again.")
            return False
        else:
            print("This step failed but is not critical. Continuing...")
            return True

def check_python_version():
    """Check if Python version is compatible."""
    print_step(1, "Checking Python version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def create_virtual_environment():
    """Create a virtual environment."""
    print_step(2, "Creating virtual environment")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("Virtual environment already exists")
        return True
    
    return run_command(
        f"{sys.executable} -m venv venv",
        "Virtual environment creation"
    )

def get_activation_command():
    """Get the appropriate activation command for the platform."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install required dependencies."""
    print_step(3, "Installing dependencies")
    
    # Get the appropriate pip command
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", "Pip upgrade", critical=False)
    
    # Install requirements
    return run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Dependencies installation"
    )

def create_data_folder():
    """Create the data folder for documents."""
    print_step(4, "Creating data folder")
    
    data_folder = Path("data")
    if not data_folder.exists():
        data_folder.mkdir()
        print("✅ Data folder created")
    else:
        print("Data folder already exists")
    
    # Copy the existing PDF if it exists in the workspace
    ml_pdf = Path("machine_learning_yearning_by_andrew_ng.pdf")
    data_ml_pdf = data_folder / "machine_learning_yearning_by_andrew_ng.pdf"
    
    if ml_pdf.exists() and not data_ml_pdf.exists():
        import shutil
        shutil.copy2(ml_pdf, data_ml_pdf)
        print("✅ Copied ML Yearning PDF to data folder")
    
    return True

def run_basic_tests():
    """Run basic tests to verify installation."""
    print_step(5, "Running basic tests")
    
    # Get the appropriate python command
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    return run_command(
        f"{python_cmd} test_chatbot.py",
        "Basic tests",
        critical=False
    )

def setup_complete_message():
    """Display setup completion message."""
    print_header("🎉 SETUP COMPLETE")
    
    activation_cmd = get_activation_command()
    
    print("Your Document Chatbot is ready to use!")
    print("\nNext steps:")
    print(f"1. Activate the virtual environment: {activation_cmd}")
    print("2. Add documents to the 'data' folder (PDF, TXT, MD, DOCX)")
    print("3. Try the system:")
    print("   • CLI: python main.py ingest data")
    print("   • Web UI: streamlit run streamlit_app.py")
    print("   • Demo: python demo.py")
    print("   • API: python fastapi_app.py")
    print("   • Notebook: jupyter notebook demo_notebook.ipynb")
    
    print("\nFor help:")
    print("   • python main.py --help")
    print("   • Check README.md for detailed instructions")
    
    print("\n📚 Happy chatting with your documents!")

def main():
    """Main setup function."""
    print_header("🤖 DOCUMENT CHATBOT SETUP")
    print("This script will help you set up the Document Chatbot system.")
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found. Please run this script from the project root directory.")
        return False
    
    # Run setup steps
    steps = [
        check_python_version,
        create_virtual_environment,
        install_dependencies,
        create_data_folder,
        run_basic_tests
    ]
    
    for step in steps:
        if not step():
            print(f"\n❌ Setup failed at step: {step.__name__}")
            print("Please fix the error and run the setup again.")
            return False
    
    setup_complete_message()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)
