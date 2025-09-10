#!/usr/bin/env python3
"""
Test runner for ModelSync
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("🧪 Running ModelSync tests...")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--color=yes"
    ], capture_output=False)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
