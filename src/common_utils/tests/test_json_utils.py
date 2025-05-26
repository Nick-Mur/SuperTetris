"""
Tests for JSON utilities.
"""

import pytest
from ..json_utils import (
    load_json,
    save_json,
    validate_json_schema,
    merge_json
)

def test_load_json(tmp_path):
    """Test loading JSON from file."""
    # Create test JSON file
    json_file = tmp_path / "test.json"
    json_file.write_text('{"test": "value"}')
    
    # Test loading
    data = load_json(str(json_file))
    assert data == {"test": "value"}
    
    # Test loading non-existent file
    with pytest.raises(FileNotFoundError):
        load_json("non_existent.json")
    
    # Test loading invalid JSON
    json_file.write_text('{"invalid": json}')
    with pytest.raises(ValueError):
        load_json(str(json_file))

def test_save_json(tmp_path):
    """Test saving JSON to file."""
    json_file = tmp_path / "test.json"
    data = {"test": "value"}
    
    # Test saving
    save_json(str(json_file), data)
    assert json_file.read_text() == '{"test": "value"}'
    
    # Test saving with indentation
    save_json(str(json_file), data, indent=2)
    assert json_file.read_text() == '{\n  "test": "value"\n}'

def test_validate_json_schema():
    """Test JSON schema validation."""
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    # Test valid data
    data = {"name": "John", "age": 30}
    assert validate_json_schema(data, schema)
    
    # Test invalid data
    data = {"age": "30"}  # Missing required field
    assert not validate_json_schema(data, schema)
    
    data = {"name": 123, "age": 30}  # Wrong type
    assert not validate_json_schema(data, schema)

def test_merge_json():
    """Test merging JSON objects."""
    # Test simple merge
    obj1 = {"a": 1, "b": 2}
    obj2 = {"c": 3, "d": 4}
    assert merge_json(obj1, obj2) == {"a": 1, "b": 2, "c": 3, "d": 4}
    
    # Test nested merge
    obj1 = {"a": {"x": 1}, "b": 2}
    obj2 = {"a": {"y": 2}, "c": 3}
    assert merge_json(obj1, obj2) == {"a": {"x": 1, "y": 2}, "b": 2, "c": 3}
    
    # Test list merge
    obj1 = {"a": [1, 2]}
    obj2 = {"a": [3, 4]}
    assert merge_json(obj1, obj2) == {"a": [1, 2, 3, 4]} 