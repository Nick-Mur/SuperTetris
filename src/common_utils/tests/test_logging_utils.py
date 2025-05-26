"""
Tests for logging utilities.
"""

import pytest
import logging
from ..logging_utils import (
    setup_logger,
    get_logger,
    log_exception,
    log_performance
)

def test_setup_logger(tmp_path):
    """Test logger setup."""
    log_file = tmp_path / "test.log"
    
    # Test basic setup
    logger = setup_logger("test", str(log_file))
    assert logger.name == "test"
    assert logger.level == logging.INFO
    
    # Test custom level
    logger = setup_logger("test", str(log_file), level=logging.DEBUG)
    assert logger.level == logging.DEBUG
    
    # Test log rotation
    logger = setup_logger("test", str(log_file), max_bytes=1000, backup_count=3)
    assert logger.handlers[0].maxBytes == 1000
    assert logger.handlers[0].backupCount == 3

def test_get_logger():
    """Test getting logger instance."""
    # Test getting existing logger
    logger1 = get_logger("test")
    logger2 = get_logger("test")
    assert logger1 is logger2
    
    # Test getting new logger
    logger3 = get_logger("test2")
    assert logger3 is not logger1

def test_log_exception(caplog):
    """Test exception logging."""
    logger = setup_logger("test")
    
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_exception(logger, e)
    
    assert "Test error" in caplog.text
    assert "ValueError" in caplog.text

def test_log_performance(caplog):
    """Test performance logging."""
    logger = setup_logger("test")
    
    @log_performance(logger)
    def test_function():
        return "test"
    
    result = test_function()
    assert result == "test"
    assert "test_function" in caplog.text
    assert "execution time" in caplog.text.lower() 