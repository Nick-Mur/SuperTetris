"""
Logging utilities for all Python services.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    format_str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    max_bytes: int = 0,
    backup_count: int = 0,
) -> logging.Logger:
    """Setup logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(format_str)

    # File handler if log_file is provided
    if log_file:
        # Ensure log directory exists
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        if max_bytes > 0:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
        else:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger by name."""
    return logging.getLogger(name)

def set_log_level(logger: logging.Logger, level: int) -> None:
    """Set log level for logger."""
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def log_exception(logger: logging.Logger, exc: Exception) -> None:
    """Log an exception with traceback."""
    logger.exception(exc)


def log_performance(logger: logging.Logger):
    """Decorator to log function execution time."""

    def decorator(func):
        from functools import wraps
        import time

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            logger.info("%s execution time %.2f ms", func.__name__, duration)
            return result

        return wrapper

    return decorator


