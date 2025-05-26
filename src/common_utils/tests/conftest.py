"""
Common fixtures for tests.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_config():
    """Create a test configuration."""
    return {
        "test": "value",
        "nested": {
            "key": "value"
        },
        "list": [1, 2, 3]
    }

@pytest.fixture
def test_logger():
    """Create a test logger."""
    import logging
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture
def test_files(temp_dir):
    """Create test files in temporary directory."""
    files = {
        "test1.txt": "content1",
        "test2.txt": "content2",
        "test3.json": '{"key": "value"}'
    }
    
    for filename, content in files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
    
    return temp_dir 