"""
Data models for the AI system.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
import numpy as np
import torch
import torch.nn as nn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

    def __post_init__(self):
        """Validate the game state after initialization."""
        if not isinstance(self.board, np.ndarray):
            raise TypeError("board must be a numpy array")
        if not isinstance(self.current_block, dict):
            raise TypeError("current_block must be a dictionary")
        if not isinstance(self.next_blocks, list):
            raise TypeError("next_blocks must be a list")
        if not isinstance(self.player_stats, dict):
            raise TypeError("player_stats must be a dictionary")
        if not isinstance(self.opponent_stats, dict):
            raise TypeError("opponent_stats must be a dictionary")
        if not isinstance(self.available_spells, list):
            raise TypeError("available_spells must be a list")
        if not isinstance(self.active_spells, list):
            raise TypeError("active_spells must be a list")
        if not isinstance(self.game_mode, str):
            raise TypeError("game_mode must be a string")
        if not isinstance(self.difficulty_level, int):
            raise TypeError("difficulty_level must be an integer")

@dataclass
class Action:
    """Represents an action that the AI can take."""
    action_type: int
    parameters: Dict[str, Any]

    def __post_init__(self):
        """Validate the action after initialization."""
        if not isinstance(self.action_type, int):
            raise TypeError("action_type must be an integer")
        if not isinstance(self.parameters, dict):
            raise TypeError("parameters must be a dictionary")

class AIPlayer:
    """Abstract base class for all AI player implementations."""
    def __init__(self, difficulty: int, name: str = "AI"):
        """Initialize the AI player.
        
        Args:
            difficulty (int): Difficulty level (1-4)
            name (str): Player name
        """
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 4:
            raise ValueError("difficulty must be an integer between 1 and 4")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
            
        self.difficulty = difficulty
        self.name = name
        logger.info(f"Created AI player {name} with difficulty {difficulty}")

    def get_action(self, state: GameState) -> Action:
        """Get the next action based on the current game state.
        
        Args:
            state (GameState): Current game state
            
        Returns:
            Action: Next action to take
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError

    def update(self, state: GameState, action: Action, reward: float, next_state: GameState):
        """Update the AI's knowledge based on the result of an action.
        
        Args:
            state (GameState): Previous game state
            action (Action): Action taken
            reward (float): Reward received
            next_state (GameState): New game state
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError

    def save(self, path: str):
        """Save the AI's state to a file.
        
        Args:
            path (str): Path to save file
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError

    def load(self, path: str):
        """Load the AI's state from a file.
        
        Args:
            path (str): Path to load file from
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError

@dataclass
class HeuristicAIPlayer(AIPlayer):
    """AI player that uses heuristic-based decision making."""
    decision_weights: Dict[str, float]
    last_decision_time: float = 0.0

    def __init__(self, difficulty: int, name: str = "HeuristicAI"):
        """Initialize the heuristic AI player.
        
        Args:
            difficulty (int): Difficulty level (1-4)
            name (str): Player name
        """
        super().__init__(difficulty, name)
        self.decision_weights = self._get_weights_for_difficulty(difficulty)
        logger.info(f"Initialized heuristic weights: {self.decision_weights}")

    def _get_weights_for_difficulty(self, difficulty: int) -> Dict[str, float]:
        """Get decision weights based on difficulty level.
        
        Args:
            difficulty (int): Difficulty level (1-4)
            
        Returns:
            Dict[str, float]: Dictionary of weights for different heuristics
        """
        weights = {
            1: {  # EASY
                "holes": 0.3,
                "bumpiness": 0.2,
                "height": 0.3,
                "lines_cleared": 0.8,
                "tower_stability": 0.4,
                "risk_taking": 0.2
            },
            2: {  # MEDIUM
                "holes": 0.5,
                "bumpiness": 0.4,
                "height": 0.5,
                "lines_cleared": 1.0,
                "tower_stability": 0.6,
                "risk_taking": 0.4
            },
            3: {  # HARD
                "holes": 0.7,
                "bumpiness": 0.6,
                "height": 0.7,
                "lines_cleared": 1.2,
                "tower_stability": 0.8,
                "risk_taking": 0.6
            },
            4: {  # EXPERT
                "holes": 0.9,
                "bumpiness": 0.8,
                "height": 0.9,
                "lines_cleared": 1.5,
                "tower_stability": 1.0,
                "risk_taking": 0.8
            }
        }
        return weights.get(difficulty, weights[4])

@dataclass
class NeuralNetAIPlayer(AIPlayer):
    """AI player that uses neural networks for decision making."""
    model: nn.Module
    epsilon: float
    memory: List[tuple]
    last_state: Optional[GameState] = None
    last_action: Optional[Action] = None
    last_reward: float = 0.0

    def __init__(self, difficulty: int, name: str = "NeuralNetAI"):
        """Initialize the neural network AI player.
        
        Args:
            difficulty (int): Difficulty level (1-4)
            name (str): Player name
        """
        super().__init__(difficulty, name)
        try:
            self.model = self._create_model()
            self.epsilon = self._get_epsilon_for_difficulty(difficulty)
            self.memory = []
            logger.info(f"Initialized neural network with epsilon {self.epsilon}")
        except Exception as e:
            logger.error(f"Failed to initialize neural network: {e}")
            raise

    def _create_model(self) -> nn.Module:
        """Create the neural network model.
        
        Returns:
            nn.Module: PyTorch neural network model
            
        Raises:
            RuntimeError: If model creation fails
        """
        try:
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
        except Exception as e:
            logger.error(f"Failed to create neural network: {e}")
            raise RuntimeError(f"Model creation failed: {e}")

    def _get_epsilon_for_difficulty(self, difficulty: int) -> float:
        """Get epsilon value based on difficulty level.
        
        Args:
            difficulty (int): Difficulty level (1-4)
            
        Returns:
            float: Epsilon value for exploration
        """
        epsilons = {
            1: 0.5,  # EASY
            2: 0.3,  # MEDIUM
            3: 0.1,  # HARD
            4: 0.05  # EXPERT
        }
        return epsilons.get(difficulty, epsilons[4])

@dataclass
class ReinforcementLearningAIPlayer(AIPlayer):
    """AI player that uses reinforcement learning for decision making."""
    model: nn.Module
    target_model: nn.Module
    epsilon: float
    epsilon_decay: float
    memory: List[tuple]
    last_state: Optional[GameState] = None
    last_action: Optional[Action] = None
    last_reward: float = 0.0
    steps: int = 0

    def __init__(self, difficulty: int, name: str = "RLPlayer"):
        """Initialize the reinforcement learning AI player.
        
        Args:
            difficulty (int): Difficulty level (1-4)
            name (str): Player name
        """
        super().__init__(difficulty, name)
        try:
            self.model = self._create_model()
            self.target_model = self._create_model()
            self.epsilon = 1.0
            self.epsilon_decay = 0.995
            self.memory = []
            self.steps = 0
            logger.info(f"Initialized RL player with epsilon {self.epsilon}")
        except Exception as e:
            logger.error(f"Failed to initialize RL player: {e}")
            raise

    def _create_model(self) -> nn.Module:
        """Create the neural network model.
        
        Returns:
            nn.Module: PyTorch neural network model
            
        Raises:
            RuntimeError: If model creation fails
        """
        try:
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
        except Exception as e:
            logger.error(f"Failed to create neural network: {e}")
            raise RuntimeError(f"Model creation failed: {e}") 