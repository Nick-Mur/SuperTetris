"""
Tests for the AI system configuration.
"""

import pytest
import os
import json
from ..src.config import (
    load_config,
    save_config,
    get_model_path,
    get_training_data_path,
    get_log_path,
    get_config_path,
    get_default_config
)

@pytest.fixture
def config():
    """Create a test configuration."""
    return {
        "model": {
            "input_size": 200,
            "hidden_layers": [128, 64],
            "output_size": 7,
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "validation_split": 0.2
        },
        "training": {
            "gamma": 0.99,
            "epsilon_start": 1.0,
            "epsilon_end": 0.01,
            "epsilon_decay": 0.995,
            "memory_capacity": 10000
        },
        "features": {
            "weight_holes": 1.0,
            "weight_bumpiness": 1.0,
            "weight_height": 1.0,
            "weight_lines": 1.0,
            "weight_holes_above": 1.0,
            "weight_well_depth": 1.0,
            "weight_row_transitions": 1.0,
            "weight_col_transitions": 1.0,
            "weight_burdened_holes": 1.0,
            "weight_well_sums": 1.0,
            "weight_hole_depth": 1.0,
            "weight_row_holes": 1.0,
            "weight_edge_adjacent_holes": 1.0,
            "weight_hole_weight": 1.0,
            "weight_landing_height": 1.0,
            "weight_eroded_piece_cells": 1.0,
            "weight_row_transitions_weight": 1.0,
            "weight_col_transitions_weight": 1.0,
            "weight_cumulative_wells": 1.0,
            "weight_well_depth_weight": 1.0,
            "weight_hole_depth_weight": 1.0,
            "weight_row_holes_weight": 1.0,
            "weight_edge_adjacent_holes_weight": 1.0,
            "weight_hole_weight_weight": 1.0,
            "weight_landing_height_weight": 1.0,
            "weight_eroded_piece_cells_weight": 1.0,
            "weight_row_transitions_weight_weight": 1.0,
            "weight_col_transitions_weight_weight": 1.0,
            "weight_cumulative_wells_weight": 1.0
        },
        "paths": {
            "model": "models",
            "training_data": "data",
            "logs": "logs",
            "config": "config"
        }
    }

def test_load_config(tmp_path, config):
    """Test loading configuration."""
    # Create test config file
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    
    # Test loading config
    loaded_config = load_config(str(config_path))
    assert loaded_config == config
    
    # Test loading non-existent config
    with pytest.raises(FileNotFoundError):
        load_config("non_existent.json")

def test_save_config(tmp_path, config):
    """Test saving configuration."""
    # Save config
    config_path = tmp_path / "config.json"
    save_config(config, str(config_path))
    
    # Verify saved config
    with open(config_path, "r") as f:
        saved_config = json.load(f)
    assert saved_config == config

def test_get_model_path(config):
    """Test getting model path."""
    model_path = get_model_path(config)
    assert isinstance(model_path, str)
    assert model_path == os.path.join(config["paths"]["model"], "model.pt")

def test_get_training_data_path(config):
    """Test getting training data path."""
    training_data_path = get_training_data_path(config)
    assert isinstance(training_data_path, str)
    assert training_data_path == os.path.join(config["paths"]["training_data"], "training_data.pt")

def test_get_log_path(config):
    """Test getting log path."""
    log_path = get_log_path(config)
    assert isinstance(log_path, str)
    assert log_path == os.path.join(config["paths"]["logs"], "ai.log")

def test_get_config_path(config):
    """Test getting config path."""
    config_path = get_config_path(config)
    assert isinstance(config_path, str)
    assert config_path == os.path.join(config["paths"]["config"], "config.json")

def test_get_default_config():
    """Test getting default configuration."""
    default_config = get_default_config()
    assert isinstance(default_config, dict)
    assert "model" in default_config
    assert "training" in default_config
    assert "features" in default_config
    assert "paths" in default_config 