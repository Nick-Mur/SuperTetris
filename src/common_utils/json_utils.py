"""
JSON utilities for all Python services.
"""

import json
from typing import Any, Dict, Optional
from pathlib import Path

from jsonschema import validate, ValidationError as JSONSchemaError

def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path: str, data: Dict[str, Any], indent: int = 0) -> None:
    """Save data to JSON file."""
    actual_indent: Optional[int] = indent if indent > 0 else None
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=actual_indent, ensure_ascii=False)

def parse_json(json_str: str) -> Dict[str, Any]:
    """Parse JSON string."""
    return json.loads(json_str)

def to_json(data: Any, indent: Optional[int] = None) -> str:
    """Convert data to JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False)

def ensure_json_dir(dir_path: str) -> None:
    """Ensure directory exists for JSON files."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate JSON data against a JSON schema."""
    try:
        validate(data, schema)
        return True
    except JSONSchemaError:
        return False


def merge_json(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two JSON-like dictionaries."""
    result = obj1.copy()
    for key, value in obj2.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge_json(result[key], value)
        elif (
            key in result
            and isinstance(result[key], list)
            and isinstance(value, list)
        ):
            result[key] = result[key] + value
        else:
            result[key] = value
    return result
