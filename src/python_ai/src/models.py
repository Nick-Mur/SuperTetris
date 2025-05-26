"""
Data models for the AI system.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np

@dataclass
class GameState:
    """Represents the current state of the game for AI decision making."""
    board: np.ndarray  # 0 for empty, positive integers for block IDs
    current_block: Dict[str, Any]
    next_blocks: List[Dict[str, Any]]
    player_stats: Dict[str, Any]
    opponent_stats: Dict[str, Any]
    available_spells: List[Dict[str, Any]]
    active_spells: List[Dict[str, Any]]
    game_mode: str
    difficulty_level: int

@dataclass
class Action:
    """Represents an action that the AI can take."""
    action_type: int
    parameters: Dict[str, Any]

class AIPlayer:
    """Abstract base class for all AI player implementations."""
    def __init__(self, difficulty: int, name: str = "AI"):
        self.difficulty = difficulty
        self.name = name

    def get_action(self, state: GameState) -> Action:
        """Get the next action based on the current game state."""
        raise NotImplementedError

    def update(self, state: GameState, action: Action, reward: float, next_state: GameState):
        """Update the AI's knowledge based on the result of an action."""
        raise NotImplementedError

    def save(self, path: str):
        """Save the AI's state to a file."""
        raise NotImplementedError

    def load(self, path: str):
        """Load the AI's state from a file."""
        raise NotImplementedError

@dataclass
class HeuristicAIPlayer(AIPlayer):
    """AI player that uses heuristic-based decision making."""
    decision_weights: Dict[str, float]
    last_decision_time: float = 0.0

    def __init__(self, difficulty: int, name: str = "HeuristicAI"):
        super().__init__(difficulty, name)
        self.decision_weights = self._get_weights_for_difficulty(difficulty)

    def _get_weights_for_difficulty(self, difficulty: int) -> Dict[str, float]:
        """Get decision weights based on difficulty level."""
        if difficulty == 1:  # EASY
            return {
                "holes": 0.3,
                "bumpiness": 0.2,
                "height": 0.3,
                "lines_cleared": 0.8,
                "tower_stability": 0.4,
                "risk_taking": 0.2
            }
        elif difficulty == 2:  # MEDIUM
            return {
                "holes": 0.5,
                "bumpiness": 0.4,
                "height": 0.5,
                "lines_cleared": 1.0,
                "tower_stability": 0.6,
                "risk_taking": 0.4
            }
        elif difficulty == 3:  # HARD
            return {
                "holes": 0.7,
                "bumpiness": 0.6,
                "height": 0.7,
                "lines_cleared": 1.2,
                "tower_stability": 0.8,
                "risk_taking": 0.6
            }
        else:  # EXPERT
            return {
                "holes": 0.9,
                "bumpiness": 0.8,
                "height": 0.9,
                "lines_cleared": 1.5,
                "tower_stability": 1.0,
                "risk_taking": 0.8
            }

@dataclass
class NeuralNetAIPlayer(AIPlayer):
    """AI player that uses neural networks for decision making."""
    model: Any  # PyTorch model
    epsilon: float
    memory: List[tuple]
    last_state: Optional[GameState] = None
    last_action: Optional[Action] = None
    last_reward: float = 0.0

    def __init__(self, difficulty: int, name: str = "NeuralNetAI"):
        super().__init__(difficulty, name)
        self.model = self._create_model()
        self.epsilon = self._get_epsilon_for_difficulty(difficulty)
        self.memory = []

    def _create_model(self):
        """Create the neural network model."""
        import torch
        import torch.nn as nn

        class TetrisNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(200, 256),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 7),
                    nn.Softmax(dim=1)
                )

            def forward(self, x):
                return self.layers(x)

        return TetrisNet()

    def _get_epsilon_for_difficulty(self, difficulty: int) -> float:
        """Get epsilon value based on difficulty level."""
        if difficulty == 1:  # EASY
            return 0.5
        elif difficulty == 2:  # MEDIUM
            return 0.3
        elif difficulty == 3:  # HARD
            return 0.1
        else:  # EXPERT
            return 0.05

@dataclass
class ReinforcementLearningAIPlayer(AIPlayer):
    """AI player that uses reinforcement learning for decision making."""
    model: Any  # PyTorch model
    target_model: Any  # PyTorch model
    epsilon: float
    epsilon_decay: float
    memory: List[tuple]
    last_state: Optional[GameState] = None
    last_action: Optional[Action] = None
    last_reward: float = 0.0
    steps: int = 0

    def __init__(self, difficulty: int, name: str = "RLPlayer"):
        super().__init__(difficulty, name)
        self.model = self._create_model()
        self.target_model = self._create_model()
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.memory = []
        self.steps = 0

    def _create_model(self):
        """Create the neural network model."""
        import torch
        import torch.nn as nn

        class TetrisNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(200, 256),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 7)
                )

            def forward(self, x):
                return self.layers(x)

        return TetrisNet() 