#!/usr/bin/env python3
"""
Development setup script for ModelSync
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False

def setup_development_environment():
    """Setup development environment"""
    print("🚀 Setting up ModelSync development environment...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        sys.exit(1)
    
    # Install development dependencies
    dev_deps = [
        "black",
        "flake8", 
        "mypy",
        "pre-commit"
    ]
    
    for dep in dev_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️  Warning: Failed to install {dep}")
    
    # Create .gitignore if it doesn't exist
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        gitignore_content = """# ModelSync
.modelsync/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Model files (examples)
*.pkl
*.joblib
*.h5
*.hdf5
*.pb
*.onnx
*.pt
*.pth
"""
        gitignore_path.write_text(gitignore_content)
        print("✅ Created .gitignore file")
    
    # Run tests
    print("\n🧪 Running tests...")
    if run_command("python run_tests.py", "Running tests"):
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed, but setup continues...")
    
    print("\n🎉 Development environment setup complete!")
    print("\nNext steps:")
    print("1. Initialize a repository: python modelsync/cli/main.py init")
    print("2. Start the API server: python modelsync/api/main.py")
    print("3. Run tests: python run_tests.py")

if __name__ == "__main__":
    setup_development_environment()
