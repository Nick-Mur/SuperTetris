"""
Configuration utilities for all Python services.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from .json_utils import load_json, save_json

class Config:
    """Configuration manager."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration optionally backed by a file."""
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        if self.config_path:
            self.load()

    def load(self) -> None:
        """Load configuration from file if path provided."""
        if not self.config_path:
            self.config = {}
            return
        if not os.path.exists(self.config_path):
            self.config = {}
            return
        self.config = load_json(self.config_path)

    def save(self) -> None:
        """Save configuration to file if path provided."""
        if self.config_path:
            save_json(self.config, self.config_path)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Return entire configuration dictionary."""
        return dict(self.config)

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

def get_env_var(key: str, default: Optional[str] = None, *, required: bool = False) -> str:
    """Get environment variable with optional default and required flag."""
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Environment variable '{key}' is required")
    return value

def set_env_var(key: str, value: str) -> None:
    """Set environment variable."""
    os.environ[key] = value


def load_config(path: str) -> "Config":
    """Load configuration from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    try:
        data = load_json(path)
    except Exception as exc:  # json.JSONDecodeError etc
        raise ValueError("Invalid configuration") from exc
    cfg = Config(path)
    cfg.config = data
    return cfg


def save_config(path: str, config: "Config", indent: int = 0) -> None:
    """Save Config instance to file."""
    save_json(path, config.get_all(), indent=indent)

def ensure_config_dir(config_dir: str) -> None:
    """Ensure configuration directory exists."""
    Path(config_dir).mkdir(parents=True, exist_ok=True) 
