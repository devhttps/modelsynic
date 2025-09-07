#!/usr/bin/env python3
"""
Instalador do ModelSync
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install project dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_modelsync_command():
    """Create modelsync command in PATH"""
    print("🔧 Setting up modelsync command...")
    
    # Determine the appropriate location for the command
    if platform.system() == "Windows":
        # Windows: Add to user's Scripts directory
        scripts_dir = Path.home() / "AppData" / "Local" / "Programs" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts"
    else:
        # Unix-like systems: Add to user's local bin
        scripts_dir = Path.home() / ".local" / "bin"
    
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create wrapper script
    wrapper_content = f"""#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modelsync.cli.main import app

if __name__ == "__main__":
    app()
"""
    
    wrapper_path = scripts_dir / "modelsync"
    if platform.system() == "Windows":
        wrapper_path = scripts_dir / "modelsync.bat"
        wrapper_content = f"""@echo off
python "{Path(__file__).parent / 'modelsync'}" %*
"""
    
    wrapper_path.write_text(wrapper_content)
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(wrapper_path, 0o755)
    
    print(f"✅ modelsync command created at: {wrapper_path}")
    return True

def run_tests():
    """Run tests to verify installation"""
    print("🧪 Running tests...")
    try:
        result = subprocess.run([
            sys.executable, "run_tests.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed, but installation continues...")
            print(f"   Test output: {result.stdout}")
            return False
    except Exception as e:
        print(f"⚠️  Could not run tests: {e}")
        return False

def show_usage_instructions():
    """Show usage instructions"""
    print("\n🎉 ModelSync installed successfully!")
    print("\n📚 Usage Instructions:")
    print("=" * 50)
    
    print("\n1️⃣ Initialize a repository:")
    print("   modelsync init --name 'Your Name' --email 'your@email.com'")
    
    print("\n2️⃣ Add files to staging:")
    print("   modelsync add file1.py file2.json")
    
    print("\n3️⃣ Create a commit:")
    print("   modelsync commit -m 'Your commit message'")
    
    print("\n4️⃣ Check status:")
    print("   modelsync status")
    
    print("\n5️⃣ View commit history:")
    print("   modelsync log")
    print("   modelsync log --oneline")
    
    print("\n6️⃣ Start API server:")
    print("   python modelsync/api/main.py")
    print("   # API will be available at: http://localhost:8000")
    print("   # Documentation at: http://localhost:8000/docs")
    
    print("\n7️⃣ Run example:")
    print("   python examples/basic_usage.py")
    
    print("\n📖 For more information:")
    print("   - README.md - Project overview")
    print("   - ARCHITECTURE.md - Technical details")
    print("   - modelsync --help - CLI help")

def main():
    """Main installation function"""
    print("🚀 ModelSync Installer")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create modelsync command
    if not create_modelsync_command():
        print("⚠️  Warning: Could not create modelsync command")
    
    # Run tests
    run_tests()
    
    # Show usage instructions
    show_usage_instructions()

if __name__ == "__main__":
    main()
