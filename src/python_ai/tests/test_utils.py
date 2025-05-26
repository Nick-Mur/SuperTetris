"""
Tests for the AI system utilities.
"""

import pytest
import numpy as np
import torch
from ..src.utils import (
    preprocess_state,
    calculate_reward,
    get_feature_vector,
    calculate_holes,
    calculate_bumpiness,
    calculate_height,
    calculate_lines,
    calculate_holes_above,
    calculate_well_depth,
    calculate_row_transitions,
    calculate_col_transitions,
    calculate_burdened_holes,
    calculate_well_sums,
    calculate_hole_depth,
    calculate_row_holes,
    calculate_edge_adjacent_holes,
    calculate_hole_weight,
    calculate_landing_height,
    calculate_eroded_piece_cells,
    calculate_row_transitions_weight,
    calculate_col_transitions_weight,
    calculate_cumulative_wells,
    calculate_well_depth_weight,
    calculate_hole_depth_weight,
    calculate_row_holes_weight,
    calculate_edge_adjacent_holes_weight,
    calculate_hole_weight_weight,
    calculate_landing_height_weight,
    calculate_eroded_piece_cells_weight,
    calculate_row_transitions_weight_weight,
    calculate_col_transitions_weight_weight,
    calculate_cumulative_wells_weight
)

@pytest.fixture
def board():
    """Create a test board."""
    return np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ], dtype=np.int32)

def test_preprocess_state(board):
    """Test state preprocessing."""
    state = preprocess_state(board)
    assert isinstance(state, np.ndarray)
    assert state.shape == (200,)
    assert state.dtype == np.float32

def test_calculate_reward():
    """Test reward calculation."""
    reward = calculate_reward(
        lines_cleared=2,
        holes_created=1,
        height_increase=2,
        game_over=False
    )
    assert isinstance(reward, float)

def test_get_feature_vector(board):
    """Test feature vector calculation."""
    features = get_feature_vector(board)
    assert isinstance(features, np.ndarray)
    assert len(features) > 0

def test_calculate_holes(board):
    """Test holes calculation."""
    holes = calculate_holes(board)
    assert isinstance(holes, int)
    assert holes >= 0

def test_calculate_bumpiness(board):
    """Test bumpiness calculation."""
    bumpiness = calculate_bumpiness(board)
    assert isinstance(bumpiness, int)
    assert bumpiness >= 0

def test_calculate_height(board):
    """Test height calculation."""
    height = calculate_height(board)
    assert isinstance(height, int)
    assert height >= 0

def test_calculate_lines(board):
    """Test lines calculation."""
    lines = calculate_lines(board)
    assert isinstance(lines, int)
    assert lines >= 0

def test_calculate_holes_above(board):
    """Test holes above calculation."""
    holes_above = calculate_holes_above(board)
    assert isinstance(holes_above, int)
    assert holes_above >= 0

def test_calculate_well_depth(board):
    """Test well depth calculation."""
    well_depth = calculate_well_depth(board)
    assert isinstance(well_depth, int)
    assert well_depth >= 0

def test_calculate_row_transitions(board):
    """Test row transitions calculation."""
    row_transitions = calculate_row_transitions(board)
    assert isinstance(row_transitions, int)
    assert row_transitions >= 0

def test_calculate_col_transitions(board):
    """Test column transitions calculation."""
    col_transitions = calculate_col_transitions(board)
    assert isinstance(col_transitions, int)
    assert col_transitions >= 0

def test_calculate_burdened_holes(board):
    """Test burdened holes calculation."""
    burdened_holes = calculate_burdened_holes(board)
    assert isinstance(burdened_holes, int)
    assert burdened_holes >= 0

def test_calculate_well_sums(board):
    """Test well sums calculation."""
    well_sums = calculate_well_sums(board)
    assert isinstance(well_sums, int)
    assert well_sums >= 0

def test_calculate_hole_depth(board):
    """Test hole depth calculation."""
    hole_depth = calculate_hole_depth(board)
    assert isinstance(hole_depth, int)
    assert hole_depth >= 0

def test_calculate_row_holes(board):
    """Test row holes calculation."""
    row_holes = calculate_row_holes(board)
    assert isinstance(row_holes, int)
    assert row_holes >= 0

def test_calculate_edge_adjacent_holes(board):
    """Test edge adjacent holes calculation."""
    edge_adjacent_holes = calculate_edge_adjacent_holes(board)
    assert isinstance(edge_adjacent_holes, int)
    assert edge_adjacent_holes >= 0

def test_calculate_hole_weight(board):
    """Test hole weight calculation."""
    hole_weight = calculate_hole_weight(board)
    assert isinstance(hole_weight, float)
    assert hole_weight >= 0

def test_calculate_landing_height(board):
    """Test landing height calculation."""
    landing_height = calculate_landing_height(board)
    assert isinstance(landing_height, int)
    assert landing_height >= 0

def test_calculate_eroded_piece_cells(board):
    """Test eroded piece cells calculation."""
    eroded_piece_cells = calculate_eroded_piece_cells(board)
    assert isinstance(eroded_piece_cells, int)
    assert eroded_piece_cells >= 0

def test_calculate_row_transitions_weight(board):
    """Test row transitions weight calculation."""
    row_transitions_weight = calculate_row_transitions_weight(board)
    assert isinstance(row_transitions_weight, float)
    assert row_transitions_weight >= 0

def test_calculate_col_transitions_weight(board):
    """Test column transitions weight calculation."""
    col_transitions_weight = calculate_col_transitions_weight(board)
    assert isinstance(col_transitions_weight, float)
    assert col_transitions_weight >= 0

def test_calculate_cumulative_wells(board):
    """Test cumulative wells calculation."""
    cumulative_wells = calculate_cumulative_wells(board)
    assert isinstance(cumulative_wells, int)
    assert cumulative_wells >= 0

def test_calculate_well_depth_weight(board):
    """Test well depth weight calculation."""
    well_depth_weight = calculate_well_depth_weight(board)
    assert isinstance(well_depth_weight, float)
    assert well_depth_weight >= 0

def test_calculate_hole_depth_weight(board):
    """Test hole depth weight calculation."""
    hole_depth_weight = calculate_hole_depth_weight(board)
    assert isinstance(hole_depth_weight, float)
    assert hole_depth_weight >= 0

def test_calculate_row_holes_weight(board):
    """Test row holes weight calculation."""
    row_holes_weight = calculate_row_holes_weight(board)
    assert isinstance(row_holes_weight, float)
    assert row_holes_weight >= 0

def test_calculate_edge_adjacent_holes_weight(board):
    """Test edge adjacent holes weight calculation."""
    edge_adjacent_holes_weight = calculate_edge_adjacent_holes_weight(board)
    assert isinstance(edge_adjacent_holes_weight, float)
    assert edge_adjacent_holes_weight >= 0

def test_calculate_hole_weight_weight(board):
    """Test hole weight weight calculation."""
    hole_weight_weight = calculate_hole_weight_weight(board)
    assert isinstance(hole_weight_weight, float)
    assert hole_weight_weight >= 0

def test_calculate_landing_height_weight(board):
    """Test landing height weight calculation."""
    landing_height_weight = calculate_landing_height_weight(board)
    assert isinstance(landing_height_weight, float)
    assert landing_height_weight >= 0

def test_calculate_eroded_piece_cells_weight(board):
    """Test eroded piece cells weight calculation."""
    eroded_piece_cells_weight = calculate_eroded_piece_cells_weight(board)
    assert isinstance(eroded_piece_cells_weight, float)
    assert eroded_piece_cells_weight >= 0

def test_calculate_row_transitions_weight_weight(board):
    """Test row transitions weight weight calculation."""
    row_transitions_weight_weight = calculate_row_transitions_weight_weight(board)
    assert isinstance(row_transitions_weight_weight, float)
    assert row_transitions_weight_weight >= 0

def test_calculate_col_transitions_weight_weight(board):
    """Test column transitions weight weight calculation."""
    col_transitions_weight_weight = calculate_col_transitions_weight_weight(board)
    assert isinstance(col_transitions_weight_weight, float)
    assert col_transitions_weight_weight >= 0

def test_calculate_cumulative_wells_weight(board):
    """Test cumulative wells weight calculation."""
    cumulative_wells_weight = calculate_cumulative_wells_weight(board)
    assert isinstance(cumulative_wells_weight, float)
    assert cumulative_wells_weight >= 0 