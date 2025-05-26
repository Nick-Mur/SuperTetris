"""
Constants for the AI system.
"""

# AI difficulty levels
DIFFICULTY_EASY = 1
DIFFICULTY_MEDIUM = 2
DIFFICULTY_HARD = 3
DIFFICULTY_EXPERT = 4

# Neural network parameters
INPUT_SIZE = 200  # 10x20 board
HIDDEN_LAYER_SIZES = [256, 128, 64]
OUTPUT_SIZE = 7  # 7 possible actions

# Training parameters
BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 100
VALIDATION_SPLIT = 0.2

# Reinforcement learning parameters
GAMMA = 0.99  # Discount factor
EPSILON_START = 1.0
EPSILON_END = 0.1
EPSILON_DECAY = 0.995
MEMORY_CAPACITY = 10000

# Feature weights for heuristic evaluation
WEIGHT_HOLES = 0.7
WEIGHT_BUMPINESS = 0.3
WEIGHT_HEIGHT = 0.5
WEIGHT_LINES_CLEARED = 1.0
WEIGHT_TOWER_STABILITY = 0.8

# Action space
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_ROTATE_CW = 3
ACTION_ROTATE_CCW = 4
ACTION_SOFT_DROP = 5
ACTION_HARD_DROP = 6
ACTION_CAST_SPELL = 7

# Spell casting thresholds
OFFENSIVE_SPELL_THRESHOLD = 0.7
DEFENSIVE_SPELL_THRESHOLD = 0.6

# Decision making frequency (in frames)
DECISION_FREQUENCY = 5

# Path constants
MODEL_SAVE_PATH = "models/"
TRAINING_DATA_PATH = "training_data/" 