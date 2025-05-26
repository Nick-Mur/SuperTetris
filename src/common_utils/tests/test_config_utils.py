"""
Tests for configuration utilities.
"""

import pytest
import os
from ..config_utils import (
    Config,
    load_config,
    save_config,
    get_env_var,
    set_env_var
)

def test_config():
    """Test Config class."""
    config = Config()
    
    # Test setting and getting values
    config.set("test", "value")
    assert config.get("test") == "value"
    
    # Test default value
    assert config.get("nonexistent", "default") == "default"
    
    # Test updating values
    config.update({"a": 1, "b": 2})
    assert config.get("a") == 1
    assert config.get("b") == 2
    
    # Test getting all values
    assert config.get_all() == {"test": "value", "a": 1, "b": 2}

def test_load_config(tmp_path):
    """Test loading configuration."""
    # Create test config file
    config_file = tmp_path / "config.json"
    config_file.write_text('{"test": "value"}')
    
    # Test loading
    config = load_config(str(config_file))
    assert config.get("test") == "value"
    
    # Test loading non-existent file
    with pytest.raises(FileNotFoundError):
        load_config("non_existent.json")
    
    # Test loading invalid config
    config_file.write_text('{"invalid": json}')
    with pytest.raises(ValueError):
        load_config(str(config_file))

def test_save_config(tmp_path):
    """Test saving configuration."""
    config_file = tmp_path / "config.json"
    config = Config()
    config.set("test", "value")
    
    # Test saving
    save_config(str(config_file), config)
    assert config_file.read_text() == '{"test": "value"}'
    
    # Test saving with indentation
    save_config(str(config_file), config, indent=2)
    assert config_file.read_text() == '{\n  "test": "value"\n}'

def test_env_vars():
    """Test environment variable utilities."""
    # Test setting and getting env var
    set_env_var("TEST_VAR", "test_value")
    assert get_env_var("TEST_VAR") == "test_value"
    
    # Test default value
    assert get_env_var("NONEXISTENT", "default") == "default"
    
    # Test required env var
    with pytest.raises(ValueError):
        get_env_var("NONEXISTENT", required=True)
    
    # Cleanup
    os.environ.pop("TEST_VAR", None) 