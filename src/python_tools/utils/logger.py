"""
Logging Utilities
"""

import logging
from pathlib import Path
from rich.logging import RichHandler
from typing import Optional

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up a logger with rich formatting
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler with rich formatting
    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setFormatter(
        logging.Formatter("%(message)s", datefmt="[%X]")
    )
    logger.addHandler(console_handler)
    
    # File handler if log file specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(file_handler)
    
    return logger 