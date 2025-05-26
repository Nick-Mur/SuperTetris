"""
Constants for the AI system.

This module defines all constants used throughout the AI system, including:
- Difficulty levels
- Neural network architecture parameters
- Training hyperparameters
- Reinforcement learning parameters
- Feature weights for heuristic evaluation
- Action space definitions
- Spell casting thresholds
- System paths
"""

from typing import List, Dict, Final
import os

# ===== Difficulty Levels =====
DIFFICULTY_EASY: Final[int] = 1
DIFFICULTY_MEDIUM: Final[int] = 2
DIFFICULTY_HARD: Final[int] = 3
DIFFICULTY_EXPERT: Final[int] = 4

# Validate difficulty levels
assert DIFFICULTY_EASY < DIFFICULTY_MEDIUM < DIFFICULTY_HARD < DIFFICULTY_EXPERT, \
    "Difficulty levels must be in ascending order"

# ===== Neural Network Architecture =====
INPUT_SIZE: Final[int] = 200  # 10x20 board
HIDDEN_LAYER_SIZES: Final[List[int]] = [256, 128, 64]
OUTPUT_SIZE: Final[int] = 7  # 7 possible actions

# Validate network architecture
assert INPUT_SIZE > 0, "Input size must be positive"
assert all(size > 0 for size in HIDDEN_LAYER_SIZES), "Hidden layer sizes must be positive"
assert OUTPUT_SIZE > 0, "Output size must be positive"

# ===== Training Parameters =====
BATCH_SIZE: Final[int] = 32
LEARNING_RATE: Final[float] = 0.001
EPOCHS: Final[int] = 100
VALIDATION_SPLIT: Final[float] = 0.2

# Validate training parameters
assert BATCH_SIZE > 0, "Batch size must be positive"
assert 0 < LEARNING_RATE < 1, "Learning rate must be between 0 and 1"
assert EPOCHS > 0, "Number of epochs must be positive"
assert 0 < VALIDATION_SPLIT < 1, "Validation split must be between 0 and 1"

# ===== Reinforcement Learning Parameters =====
GAMMA: Final[float] = 0.99  # Discount factor
EPSILON_START: Final[float] = 1.0
EPSILON_END: Final[float] = 0.1
EPSILON_DECAY: Final[float] = 0.995
MEMORY_CAPACITY: Final[int] = 10000

# Validate RL parameters
assert 0 < GAMMA < 1, "Discount factor must be between 0 and 1"
assert 0 <= EPSILON_END <= EPSILON_START <= 1, "Invalid epsilon values"
assert 0 < EPSILON_DECAY < 1, "Epsilon decay must be between 0 and 1"
assert MEMORY_CAPACITY > 0, "Memory capacity must be positive"

# ===== Feature Weights =====
WEIGHT_HOLES: Final[float] = 0.7
WEIGHT_BUMPINESS: Final[float] = 0.3
WEIGHT_HEIGHT: Final[float] = 0.5
WEIGHT_LINES_CLEARED: Final[float] = 1.0
WEIGHT_TOWER_STABILITY: Final[float] = 0.8

# Validate feature weights
assert all(0 <= w <= 1 for w in [
    WEIGHT_HOLES,
    WEIGHT_BUMPINESS,
    WEIGHT_HEIGHT,
    WEIGHT_LINES_CLEARED,
    WEIGHT_TOWER_STABILITY
]), "Feature weights must be between 0 and 1"

# ===== Action Space =====
ACTION_MOVE_LEFT: Final[int] = 1
ACTION_MOVE_RIGHT: Final[int] = 2
ACTION_ROTATE_CW: Final[int] = 3
ACTION_ROTATE_CCW: Final[int] = 4
ACTION_SOFT_DROP: Final[int] = 5
ACTION_HARD_DROP: Final[int] = 6
ACTION_CAST_SPELL: Final[int] = 7

# Validate action space
assert len(set([
    ACTION_MOVE_LEFT,
    ACTION_MOVE_RIGHT,
    ACTION_ROTATE_CW,
    ACTION_ROTATE_CCW,
    ACTION_SOFT_DROP,
    ACTION_HARD_DROP,
    ACTION_CAST_SPELL
])) == 7, "Action IDs must be unique"

# ===== Spell Casting Thresholds =====
OFFENSIVE_SPELL_THRESHOLD: Final[float] = 0.7
DEFENSIVE_SPELL_THRESHOLD: Final[float] = 0.6

# Validate spell thresholds
assert 0 <= OFFENSIVE_SPELL_THRESHOLD <= 1, "Offensive spell threshold must be between 0 and 1"
assert 0 <= DEFENSIVE_SPELL_THRESHOLD <= 1, "Defensive spell threshold must be between 0 and 1"

# ===== System Parameters =====
DECISION_FREQUENCY: Final[int] = 5  # Decision making frequency (in frames)

# Validate system parameters
assert DECISION_FREQUENCY > 0, "Decision frequency must be positive"

# ===== Path Constants =====
MODEL_SAVE_PATH: Final[str] = os.path.join(os.path.dirname(__file__), "..", "models")
TRAINING_DATA_PATH: Final[str] = os.path.join(os.path.dirname(__file__), "..", "training_data")

# Create directories if they don't exist
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
os.makedirs(TRAINING_DATA_PATH, exist_ok=True) 