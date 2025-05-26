"""
Tests for the AI system constants.
"""

import pytest
from ..src.constants import *

def test_difficulty_levels():
    """Test difficulty level constants."""
    assert DIFFICULTY_EASY == 1
    assert DIFFICULTY_MEDIUM == 2
    assert DIFFICULTY_HARD == 3
    assert DIFFICULTY_EXPERT == 4

def test_neural_network_params():
    """Test neural network parameter constants."""
    assert isinstance(INPUT_SIZE, int)
    assert isinstance(HIDDEN_LAYER_SIZES, tuple)
    assert isinstance(OUTPUT_SIZE, int)
    assert len(HIDDEN_LAYER_SIZES) > 0
    assert all(isinstance(size, int) for size in HIDDEN_LAYER_SIZES)

def test_training_params():
    """Test training parameter constants."""
    assert isinstance(BATCH_SIZE, int)
    assert BATCH_SIZE > 0
    assert isinstance(LEARNING_RATE, float)
    assert 0 < LEARNING_RATE < 1
    assert isinstance(EPOCHS, int)
    assert EPOCHS > 0
    assert isinstance(VALIDATION_SPLIT, float)
    assert 0 < VALIDATION_SPLIT < 1

def test_rl_params():
    """Test reinforcement learning parameter constants."""
    assert isinstance(GAMMA, float)
    assert 0 < GAMMA < 1
    assert isinstance(EPSILON_START, float)
    assert 0 < EPSILON_START <= 1
    assert isinstance(EPSILON_END, float)
    assert 0 <= EPSILON_END < EPSILON_START
    assert isinstance(EPSILON_DECAY, float)
    assert 0 < EPSILON_DECAY < 1
    assert isinstance(MEMORY_CAPACITY, int)
    assert MEMORY_CAPACITY > 0

def test_feature_weights():
    """Test feature weight constants."""
    assert isinstance(WEIGHT_HOLES, float)
    assert isinstance(WEIGHT_BUMPINESS, float)
    assert isinstance(WEIGHT_HEIGHT, float)
    assert isinstance(WEIGHT_LINES, float)
    assert isinstance(WEIGHT_HOLES_ABOVE, float)
    assert isinstance(WEIGHT_WELL_DEPTH, float)
    assert isinstance(WEIGHT_ROW_TRANSITIONS, float)
    assert isinstance(WEIGHT_COL_TRANSITIONS, float)
    assert isinstance(WEIGHT_BURDENED_HOLES, float)
    assert isinstance(WEIGHT_WELL_SUMS, float)
    assert isinstance(WEIGHT_HOLE_DEPTH, float)
    assert isinstance(WEIGHT_ROW_HOLES, float)
    assert isinstance(WEIGHT_EDGE_ADJACENT_HOLES, float)
    assert isinstance(WEIGHT_HOLE_WEIGHT, float)
    assert isinstance(WEIGHT_LANDING_HEIGHT, float)
    assert isinstance(WEIGHT_ERODED_PIECE_CELLS, float)
    assert isinstance(WEIGHT_ROW_TRANSITIONS_WEIGHT, float)
    assert isinstance(WEIGHT_COL_TRANSITIONS_WEIGHT, float)
    assert isinstance(WEIGHT_CUMULATIVE_WELLS, float)
    assert isinstance(WEIGHT_WELL_DEPTH_WEIGHT, float)
    assert isinstance(WEIGHT_HOLE_DEPTH_WEIGHT, float)
    assert isinstance(WEIGHT_ROW_HOLES_WEIGHT, float)
    assert isinstance(WEIGHT_EDGE_ADJACENT_HOLES_WEIGHT, float)
    assert isinstance(WEIGHT_HOLE_WEIGHT_WEIGHT, float)
    assert isinstance(WEIGHT_LANDING_HEIGHT_WEIGHT, float)
    assert isinstance(WEIGHT_ERODED_PIECE_CELLS_WEIGHT, float)
    assert isinstance(WEIGHT_ROW_TRANSITIONS_WEIGHT_WEIGHT, float)
    assert isinstance(WEIGHT_COL_TRANSITIONS_WEIGHT_WEIGHT, float)
    assert isinstance(WEIGHT_CUMULATIVE_WELLS_WEIGHT, float)

def test_action_space():
    """Test action space constants."""
    assert ACTION_MOVE_LEFT == 1
    assert ACTION_MOVE_RIGHT == 2
    assert ACTION_ROTATE_CW == 3
    assert ACTION_ROTATE_CCW == 4
    assert ACTION_SOFT_DROP == 5
    assert ACTION_HARD_DROP == 6
    assert ACTION_HOLD == 7

def test_spell_thresholds():
    """Test spell threshold constants."""
    assert isinstance(OFFENSIVE_SPELL_THRESHOLD, float)
    assert 0 < OFFENSIVE_SPELL_THRESHOLD < 1
    assert isinstance(DEFENSIVE_SPELL_THRESHOLD, float)
    assert 0 < DEFENSIVE_SPELL_THRESHOLD < 1

def test_decision_frequency():
    """Test decision frequency constant."""
    assert isinstance(DECISION_FREQUENCY, int)
    assert DECISION_FREQUENCY > 0

def test_paths():
    """Test path constants."""
    assert isinstance(MODEL_PATH, str)
    assert isinstance(TRAINING_DATA_PATH, str) 