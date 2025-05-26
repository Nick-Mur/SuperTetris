"""
Tests for the AI models.
"""

import pytest
import numpy as np
import torch
from ..src.models import (
    GameState,
    Action,
    HeuristicAIPlayer,
    NeuralNetAIPlayer,
    ReinforcementLearningAIPlayer
)
from ..src.constants import *

@pytest.fixture
def game_state():
    """Create a test game state."""
    return GameState(
        board=np.zeros((20, 10), dtype=np.int32),
        current_block={"type": "I", "rotation": 0, "x": 5, "y": 0},
        next_blocks=[{"type": "O", "rotation": 0}],
        player_stats={"score": 0, "lines_cleared": 0},
        opponent_stats={"score": 0, "lines_cleared": 0},
        available_spells=[],
        active_spells=[],
        game_mode="classic",
        difficulty_level=1
    )

def test_game_state(game_state):
    """Test GameState class."""
    assert isinstance(game_state.board, np.ndarray)
    assert game_state.board.shape == (20, 10)
    assert isinstance(game_state.current_block, dict)
    assert isinstance(game_state.next_blocks, list)
    assert isinstance(game_state.player_stats, dict)
    assert isinstance(game_state.opponent_stats, dict)
    assert isinstance(game_state.available_spells, list)
    assert isinstance(game_state.active_spells, list)
    assert isinstance(game_state.game_mode, str)
    assert isinstance(game_state.difficulty_level, int)

def test_action():
    """Test Action class."""
    action = Action(ACTION_MOVE_LEFT, {"x": 1})
    assert action.action_type == ACTION_MOVE_LEFT
    assert action.parameters == {"x": 1}

def test_heuristic_player(game_state):
    """Test HeuristicAIPlayer class."""
    player = HeuristicAIPlayer("test", DIFFICULTY_EASY)
    
    # Test getting action
    action = player.get_action(game_state)
    assert isinstance(action, Action)
    assert action.action_type in range(1, 8)
    
    # Test updating knowledge
    next_state = GameState(
        board=np.zeros((20, 10), dtype=np.int32),
        current_block={"type": "I", "rotation": 0, "x": 4, "y": 0},
        next_blocks=[{"type": "O", "rotation": 0}],
        player_stats={"score": 10, "lines_cleared": 0},
        opponent_stats={"score": 0, "lines_cleared": 0},
        available_spells=[],
        active_spells=[],
        game_mode="classic",
        difficulty_level=1
    )
    player.update(game_state, Action(ACTION_MOVE_LEFT, {}), 1.0, next_state)
    
    # Test saving and loading
    player.save("test_heuristic.pt")
    loaded_player = HeuristicAIPlayer("test", DIFFICULTY_EASY)
    loaded_player.load("test_heuristic.pt")
    assert loaded_player.name == player.name
    assert loaded_player.difficulty == player.difficulty

def test_neural_net_player(game_state):
    """Test NeuralNetAIPlayer class."""
    player = NeuralNetAIPlayer("test", DIFFICULTY_MEDIUM)
    
    # Test getting action
    action = player.get_action(game_state)
    assert isinstance(action, Action)
    assert action.action_type in range(1, 8)
    
    # Test updating knowledge
    next_state = GameState(
        board=np.zeros((20, 10), dtype=np.int32),
        current_block={"type": "I", "rotation": 0, "x": 4, "y": 0},
        next_blocks=[{"type": "O", "rotation": 0}],
        player_stats={"score": 10, "lines_cleared": 0},
        opponent_stats={"score": 0, "lines_cleared": 0},
        available_spells=[],
        active_spells=[],
        game_mode="classic",
        difficulty_level=1
    )
    player.update(game_state, Action(ACTION_MOVE_LEFT, {}), 1.0, next_state)
    
    # Test saving and loading
    player.save("test_neural.pt")
    loaded_player = NeuralNetAIPlayer("test", DIFFICULTY_MEDIUM)
    loaded_player.load("test_neural.pt")
    assert loaded_player.name == player.name
    assert loaded_player.difficulty == player.difficulty
    
    # Test model creation
    model = player._create_model()
    assert isinstance(model, torch.nn.Module)
    assert len(list(model.parameters())) > 0

def test_rl_player(game_state):
    """Test ReinforcementLearningAIPlayer class."""
    player = ReinforcementLearningAIPlayer("test", DIFFICULTY_HARD)
    
    # Test getting action
    action = player.get_action(game_state)
    assert isinstance(action, Action)
    assert action.action_type in range(1, 8)
    
    # Test updating knowledge
    next_state = GameState(
        board=np.zeros((20, 10), dtype=np.int32),
        current_block={"type": "I", "rotation": 0, "x": 4, "y": 0},
        next_blocks=[{"type": "O", "rotation": 0}],
        player_stats={"score": 10, "lines_cleared": 0},
        opponent_stats={"score": 0, "lines_cleared": 0},
        available_spells=[],
        active_spells=[],
        game_mode="classic",
        difficulty_level=1
    )
    player.update(game_state, Action(ACTION_MOVE_LEFT, {}), 1.0, next_state)
    
    # Test saving and loading
    player.save("test_rl.pt")
    loaded_player = ReinforcementLearningAIPlayer("test", DIFFICULTY_HARD)
    loaded_player.load("test_rl.pt")
    assert loaded_player.name == player.name
    assert loaded_player.difficulty == player.difficulty
    
    # Test memory management
    for _ in range(MEMORY_CAPACITY + 10):
        player._add_to_memory(
            np.random.rand(200),
            np.random.randint(1, 8),
            np.random.rand(),
            np.random.rand(200)
        )
    assert len(player.memory) == MEMORY_CAPACITY
    
    # Test epsilon decay
    initial_epsilon = player.epsilon
    player._update_epsilon()
    assert player.epsilon < initial_epsilon 