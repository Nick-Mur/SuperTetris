"""
File utilities for all Python services.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional

def ensure_dir(dir_path: str) -> None:
    """Ensure directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def list_files(dir_path: str, pattern: str = "*", recursive: bool = False) -> List[str]:
    """List files in directory matching pattern."""
    path = Path(dir_path)
    if recursive:
        paths = path.rglob(pattern)
    else:
        paths = path.glob(pattern)
    return [str(p) for p in paths if p.is_file()]

def copy_file(src: str, dst: str) -> None:
    """Copy file from src to dst."""
    shutil.copy2(src, dst)

def move_file(src: str, dst: str) -> None:
    """Move file from src to dst."""
    shutil.move(src, dst)

def delete_file(file_path: str) -> None:
    """Delete file."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(file_path)
    p.unlink()

def read_file(file_path: str, encoding: str = 'utf-8') -> str:
    """Read file content."""
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()

def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """Write content to file."""
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)

def append_file(file_path: str, content: str, encoding: str = 'utf-8') -> None:
    """Append content to file."""
    with open(file_path, 'a', encoding=encoding) as f:
        f.write(content)

def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    return Path(file_path).stat().st_size

def get_file_extension(file_path: str) -> str:
    """Get file extension."""
    return Path(file_path).suffix

def get_file_name(file_path: str) -> str:
    """Get file name without extension."""
    return Path(file_path).stem 

