"""Utility functions for logging and common operations."""

import logging
import sys
from pathlib import Path
from typing import Optional

from src.config import LOG_DIR, LOG_FILE


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Path to log file. If None, uses default from config.
        level: Logging level (default: INFO)
        format_string: Custom format string. If None, uses default.
    
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    # Default format
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_file = LOG_FILE
    
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

