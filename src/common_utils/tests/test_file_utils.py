"""
Tests for file utilities.
"""

import pytest
import os
import shutil
from ..file_utils import (
    ensure_dir,
    list_files,
    read_file,
    write_file,
    copy_file,
    move_file,
    delete_file
)

def test_ensure_dir(tmp_path):
    """Test directory creation."""
    test_dir = tmp_path / "test_dir"
    
    # Test creating new directory
    ensure_dir(str(test_dir))
    assert test_dir.exists()
    assert test_dir.is_dir()
    
    # Test creating existing directory
    ensure_dir(str(test_dir))
    assert test_dir.exists()

def test_list_files(tmp_path):
    """Test file listing."""
    # Create test files
    (tmp_path / "test1.txt").write_text("test1")
    (tmp_path / "test2.txt").write_text("test2")
    (tmp_path / "test3.json").write_text("{}")
    
    # Test listing all files
    files = list_files(str(tmp_path))
    assert len(files) == 3
    
    # Test listing with pattern
    txt_files = list_files(str(tmp_path), pattern="*.txt")
    assert len(txt_files) == 2
    
    # Test listing with recursive
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "test4.txt").write_text("test4")
    
    all_files = list_files(str(tmp_path), recursive=True)
    assert len(all_files) == 4

def test_read_write_file(tmp_path):
    """Test file reading and writing."""
    test_file = tmp_path / "test.txt"
    
    # Test writing file
    write_file(str(test_file), "test content")
    assert test_file.read_text() == "test content"
    
    # Test reading file
    content = read_file(str(test_file))
    assert content == "test content"
    
    # Test reading non-existent file
    with pytest.raises(FileNotFoundError):
        read_file("non_existent.txt")

def test_copy_move_file(tmp_path):
    """Test file copying and moving."""
    source = tmp_path / "source.txt"
    source.write_text("test content")
    
    # Test copying file
    dest = tmp_path / "dest.txt"
    copy_file(str(source), str(dest))
    assert dest.exists()
    assert dest.read_text() == "test content"
    
    # Test moving file
    move_dest = tmp_path / "moved.txt"
    move_file(str(source), str(move_dest))
    assert not source.exists()
    assert move_dest.exists()
    assert move_dest.read_text() == "test content"

def test_delete_file(tmp_path):
    """Test file deletion."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    # Test deleting file
    delete_file(str(test_file))
    assert not test_file.exists()
    
    # Test deleting non-existent file
    with pytest.raises(FileNotFoundError):
        delete_file("non_existent.txt") 