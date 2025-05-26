"""
JSON utilities for all Python services.
"""

import json
from typing import Any, Dict, Optional
from pathlib import Path

def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON from file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def parse_json(json_str: str) -> Dict[str, Any]:
    """Parse JSON string."""
    return json.loads(json_str)

def to_json(data: Any, indent: Optional[int] = None) -> str:
    """Convert data to JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False)

def ensure_json_dir(dir_path: str) -> None:
    """Ensure directory exists for JSON files."""
    Path(dir_path).mkdir(parents=True, exist_ok=True) 