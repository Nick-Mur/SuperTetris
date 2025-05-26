"""
Tests for the AI system logger.
"""

import pytest
import os
import logging
from ..src.logger import (
    setup_logger,
    get_logger,
    log_info,
    log_warning,
    log_error,
    log_debug,
    log_training,
    log_evaluation,
    log_action,
    log_state
)

@pytest.fixture
def log_file(tmp_path):
    """Create a test log file."""
    return str(tmp_path / "test.log")

def test_setup_logger(log_file):
    """Test logger setup."""
    # Setup logger
    logger = setup_logger(log_file)
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
    
    # Test file handler
    assert len(logger.handlers) > 0
    file_handler = logger.handlers[0]
    assert isinstance(file_handler, logging.FileHandler)
    assert file_handler.baseFilename == log_file

def test_get_logger(log_file):
    """Test getting logger."""
    # Setup logger
    setup_logger(log_file)
    
    # Get logger
    logger = get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO

def test_log_info(log_file):
    """Test info logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log info
    log_info("Test info message")
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "INFO" in log_content
    assert "Test info message" in log_content

def test_log_warning(log_file):
    """Test warning logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log warning
    log_warning("Test warning message")
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "WARNING" in log_content
    assert "Test warning message" in log_content

def test_log_error(log_file):
    """Test error logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log error
    log_error("Test error message")
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "ERROR" in log_content
    assert "Test error message" in log_content

def test_log_debug(log_file):
    """Test debug logging."""
    # Setup logger with debug level
    logger = setup_logger(log_file, level=logging.DEBUG)
    
    # Log debug
    log_debug("Test debug message")
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "DEBUG" in log_content
    assert "Test debug message" in log_content

def test_log_training(log_file):
    """Test training logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log training
    log_training(
        epoch=1,
        batch=1,
        loss=0.5,
        accuracy=0.8,
        learning_rate=0.001
    )
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "TRAINING" in log_content
    assert "epoch=1" in log_content
    assert "batch=1" in log_content
    assert "loss=0.5" in log_content
    assert "accuracy=0.8" in log_content
    assert "learning_rate=0.001" in log_content

def test_log_evaluation(log_file):
    """Test evaluation logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log evaluation
    log_evaluation(
        player_name="test_player",
        score=100,
        lines_cleared=10,
        time_played=60
    )
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "EVALUATION" in log_content
    assert "player_name=test_player" in log_content
    assert "score=100" in log_content
    assert "lines_cleared=10" in log_content
    assert "time_played=60" in log_content

def test_log_action(log_file):
    """Test action logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log action
    log_action(
        player_name="test_player",
        action_type=1,
        parameters={"x": 1, "y": 2}
    )
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "ACTION" in log_content
    assert "player_name=test_player" in log_content
    assert "action_type=1" in log_content
    assert "parameters={'x': 1, 'y': 2}" in log_content

def test_log_state(log_file):
    """Test state logging."""
    # Setup logger
    setup_logger(log_file)
    
    # Log state
    log_state(
        player_name="test_player",
        board=[[0, 0], [0, 0]],
        score=100,
        lines_cleared=10
    )
    
    # Verify log file
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "STATE" in log_content
    assert "player_name=test_player" in log_content
    assert "board=[[0, 0], [0, 0]]" in log_content
    assert "score=100" in log_content
    assert "lines_cleared=10" in log_content 