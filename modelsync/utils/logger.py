"""
Logging utilities for ModelSync
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str = "modelsync",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logger for ModelSync"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str = "modelsync") -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
