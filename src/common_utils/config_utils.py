"""
Configuration utilities for all Python services.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from .json_utils import load_json, save_json

class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: str):
        """Initialize with config file path."""
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            self.config = load_json(self.config_path)
        else:
            self.config = {}

    def save(self) -> None:
        """Save configuration to file."""
        save_json(self.config, self.config_path)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        self.save()

    def update(self, config_dict: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        self.config.update(config_dict)
        self.save()

    def delete(self, key: str) -> None:
        """Delete configuration value."""
        if key in self.config:
            del self.config[key]
            self.save()

def get_env_var(key: str, default: Optional[str] = None) -> str:
    """Get environment variable with default value."""
    return os.getenv(key, default)

def set_env_var(key: str, value: str) -> None:
    """Set environment variable."""
    os.environ[key] = value

def ensure_config_dir(config_dir: str) -> None:
    """Ensure configuration directory exists."""
    Path(config_dir).mkdir(parents=True, exist_ok=True) 