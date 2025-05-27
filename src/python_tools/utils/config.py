"""
Configuration Utilities
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

def load_config(config_file: Path) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file) as f:
        return json.load(f)

def save_config(config: Dict[str, Any], config_file: Path) -> None:
    """
    Save configuration to JSON file
    
    Args:
        config: Configuration dictionary
        config_file: Path to save configuration to
    """
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration
    
    Returns:
        Default configuration dictionary
    """
    return {
        "editor": {
            "default_width": 10,
            "default_height": 20,
            "default_difficulty": "medium"
        },
        "generator": {
            "min_blocks": 3,
            "max_blocks": 12,
            "special_rules_probability": 0.3
        },
        "analyzer": {
            "metrics": ["score", "combo", "speed"],
            "report_format": "png"
        },
        "profiler": {
            "output_dir": "data/profiles",
            "report_dir": "data/reports"
        }
    } 