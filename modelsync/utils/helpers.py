"""
Helper utilities for ModelSync
"""

import hashlib
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (IOError, OSError):
        return ""

def calculate_content_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of content"""
    return hashlib.sha256(content).hexdigest()

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information including hash, size, and metadata"""
    path = Path(file_path)
    if not path.exists():
        return {}
    
    stat = path.stat()
    return {
        "path": str(path),
        "name": path.name,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "hash": calculate_file_hash(file_path),
        "is_file": path.is_file(),
        "is_dir": path.is_dir()
    }

def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)

def write_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Write data to JSON file"""
    ensure_directory(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_tracked_files(directory: str = ".") -> List[str]:
    """Get list of files that should be tracked by ModelSync"""
    tracked_files = []
    directory_path = Path(directory)
    
    for file_path in directory_path.rglob("*"):
        if file_path.is_file() and not str(file_path).startswith(".modelsync"):
            # Check if file extension is supported
            if file_path.suffix.lower() in {'.py', '.ipynb', '.json', '.yaml', '.yml', '.txt', '.md',
                                          '.pkl', '.joblib', '.h5', '.hdf5', '.pb', '.onnx', '.pt', '.pth',
                                          '.csv', '.tsv', '.parquet', '.feather', '.npy', '.npz'}:
                tracked_files.append(str(file_path))
    
    return tracked_files

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"