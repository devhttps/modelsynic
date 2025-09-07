"""
Configuration settings for ModelSync
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base directories
MODELSYNC_DIR = ".modelsync"
OBJECTS_DIR = ".modelsync/objects"
REFS_DIR = ".modelsync/refs"
HEADS_DIR = ".modelsync/refs/heads"
METADATA_DIR = ".modelsync/metadata"
LOGS_DIR = ".modelsync/logs"

# File paths
CONFIG_FILE = ".modelsync/config"
HEAD_FILE = ".modelsync/HEAD"
INDEX_FILE = ".modelsync/index"
HISTORY_FILE = ".modelsync/logs/history.log"

# Supported file types for AI projects
SUPPORTED_EXTENSIONS = {
    '.py', '.ipynb', '.json', '.yaml', '.yml', '.txt', '.md',
    '.pkl', '.joblib', '.h5', '.hdf5', '.pb', '.onnx', '.pt', '.pth',
    '.csv', '.tsv', '.parquet', '.feather', '.npy', '.npz'
}

# Maximum file size (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Default configuration
DEFAULT_CONFIG = {
    "core": {
        "repository_format_version": "1",
        "file_mode": "false",
        "bare": "false"
    },
    "user": {
        "name": "",
        "email": ""
    },
    "remote": {
        "origin": {
            "url": "",
            "fetch": "+refs/heads/*:refs/remotes/origin/*"
        }
    }
}

def get_config() -> Dict[str, Any]:
    """Load configuration from file or return defaults"""
    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        # TODO: Implement config file parsing
        pass
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file"""
    config_path = Path(CONFIG_FILE)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    # TODO: Implement config file writing
    pass
