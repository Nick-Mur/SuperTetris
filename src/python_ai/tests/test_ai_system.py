"""
Tests for the AI system.
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
from ..src.ai_system import AISystem
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

@pytest.fixture
def ai_system():
    """Create a test AI system."""
    return AISystem()

def test_create_player(ai_system):
    """Test creating different types of AI players."""
    # Test heuristic player
    player = ai_system.create_player("heuristic", DIFFICULTY_EASY, "test_heuristic")
    assert isinstance(player, HeuristicAIPlayer)
    assert player.name == "test_heuristic"
    assert player.difficulty == DIFFICULTY_EASY
    
    # Test neural net player
    player = ai_system.create_player("neural_net", DIFFICULTY_MEDIUM, "test_neural")
    assert isinstance(player, NeuralNetAIPlayer)
    assert player.name == "test_neural"
    assert player.difficulty == DIFFICULTY_MEDIUM
    
    # Test RL player
    player = ai_system.create_player("rl", DIFFICULTY_HARD, "test_rl")
    assert isinstance(player, ReinforcementLearningAIPlayer)
    assert player.name == "test_rl"
    assert player.difficulty == DIFFICULTY_HARD
    
    # Test invalid player type
    with pytest.raises(ValueError):
        ai_system.create_player("invalid", DIFFICULTY_EASY)

def test_get_action(ai_system, game_state):
    """Test getting actions from AI players."""
    # Create players
    heuristic_player = ai_system.create_player("heuristic", DIFFICULTY_EASY, "test_heuristic")
    neural_player = ai_system.create_player("neural_net", DIFFICULTY_MEDIUM, "test_neural")
    rl_player = ai_system.create_player("rl", DIFFICULTY_HARD, "test_rl")
    
    # Test getting actions
    action = ai_system.get_action("test_heuristic", game_state)
    assert isinstance(action, Action)
    assert action.action_type in range(1, 8)
    
    action = ai_system.get_action("test_neural", game_state)
    assert isinstance(action, Action)
    assert action.action_type in range(1, 8)
    
    action = ai_system.get_action("test_rl", game_state)
    assert isinstance(action, Action)
    assert action.action_type in range(1, 8)
    
    # Test getting action for non-existent player
    with pytest.raises(ValueError):
        ai_system.get_action("non_existent", game_state)

def test_update(ai_system, game_state):
    """Test updating AI players."""
    # Create players
    heuristic_player = ai_system.create_player("heuristic", DIFFICULTY_EASY, "test_heuristic")
    neural_player = ai_system.create_player("neural_net", DIFFICULTY_MEDIUM, "test_neural")
    rl_player = ai_system.create_player("rl", DIFFICULTY_HARD, "test_rl")
    
    # Create test action and next state
    action = Action(ACTION_MOVE_LEFT, {})
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
    
    # Test updating players
    ai_system.update("test_heuristic", game_state, action, 1.0, next_state)
    ai_system.update("test_neural", game_state, action, 1.0, next_state)
    ai_system.update("test_rl", game_state, action, 1.0, next_state)
    
    # Test updating non-existent player
    with pytest.raises(ValueError):
        ai_system.update("non_existent", game_state, action, 1.0, next_state)

def test_save_load_player(ai_system, tmp_path):
    """Test saving and loading AI players."""
    # Create players
    heuristic_player = ai_system.create_player("heuristic", DIFFICULTY_EASY, "test_heuristic")
    neural_player = ai_system.create_player("neural_net", DIFFICULTY_MEDIUM, "test_neural")
    rl_player = ai_system.create_player("rl", DIFFICULTY_HARD, "test_rl")
    
    # Save players
    save_path = tmp_path / "models"
    save_path.mkdir()
    
    ai_system.save_player("test_heuristic", str(save_path / "heuristic.pt"))
    ai_system.save_player("test_neural", str(save_path / "neural.pt"))
    ai_system.save_player("test_rl", str(save_path / "rl.pt"))
    
    # Remove players
    ai_system.remove_player("test_heuristic")
    ai_system.remove_player("test_neural")
    ai_system.remove_player("test_rl")
    
    # Load players
    ai_system.load_player("test_heuristic", str(save_path / "heuristic.pt"))
    ai_system.load_player("test_neural", str(save_path / "neural.pt"))
    ai_system.load_player("test_rl", str(save_path / "rl.pt"))
    
    # Verify loaded players
    assert isinstance(ai_system.get_player("test_heuristic"), HeuristicAIPlayer)
    assert isinstance(ai_system.get_player("test_neural"), NeuralNetAIPlayer)
    assert isinstance(ai_system.get_player("test_rl"), ReinforcementLearningAIPlayer)

def test_train_player(ai_system):
    """Test training AI players."""
    # Create neural net player
    player = ai_system.create_player("neural_net", DIFFICULTY_MEDIUM, "test_neural")
    
    # Create training data
    for _ in range(100):
        state = np.random.rand(200)
        action = np.random.randint(1, 8)
        reward = np.random.rand()
        ai_system.training_data.append((state, action, reward))
    
    # Test training
    ai_system.train_player("test_neural", epochs=2, batch_size=32)
    
    # Test training with invalid player
    with pytest.raises(ValueError):
        ai_system.train_player("non_existent")
    
    # Test training with no data
    ai_system.training_data = []
    with pytest.raises(ValueError):
        ai_system.train_player("test_neural")

def test_evaluate_player(ai_system, game_state):
    """Test evaluating AI players."""
    # Create players
    heuristic_player = ai_system.create_player("heuristic", DIFFICULTY_EASY, "test_heuristic")
    neural_player = ai_system.create_player("neural_net", DIFFICULTY_MEDIUM, "test_neural")
    rl_player = ai_system.create_player("rl", DIFFICULTY_HARD, "test_rl")
    
    # Create test data
    test_data = []
    for _ in range(10):
        state = GameState(
            board=np.random.randint(0, 2, (20, 10), dtype=np.int32),
            current_block={"type": "I", "rotation": 0, "x": 5, "y": 0},
            next_blocks=[{"type": "O", "rotation": 0}],
            player_stats={"score": 0, "lines_cleared": 0},
            opponent_stats={"score": 0, "lines_cleared": 0},
            available_spells=[],
            active_spells=[],
            game_mode="classic",
            difficulty_level=1
        )
        action = Action(np.random.randint(1, 8), {})
        reward = np.random.rand()
        test_data.append((state, action, reward))
    
    # Test evaluation
    score = ai_system.evaluate_player("test_heuristic", test_data)
    assert isinstance(score, float)
    assert 0 <= score <= 1
    
    # Test evaluation with non-existent player
    with pytest.raises(ValueError):
        ai_system.evaluate_player("non_existent", test_data) 