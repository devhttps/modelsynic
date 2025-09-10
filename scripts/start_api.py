#!/usr/bin/env python3
"""
Start ModelSync API server
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("🚀 Starting ModelSync API server...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "modelsync.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
