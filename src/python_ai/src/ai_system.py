"""
AI system implementation.
"""

import os
import json
import time
import random
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.cuda
import torch.utils.data
from typing import List, Dict, Any, Optional, Tuple
from .models import (
    GameState,
    Action,
    AIPlayer,
    HeuristicAIPlayer,
    NeuralNetAIPlayer,
    ReinforcementLearningAIPlayer
)
from .constants import *

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AISystem:
    """Main AI system class that manages AI players and training."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI system."""
        self.players: Dict[str, AIPlayer] = {}
        self.training_data: List[Tuple] = []
        self.config = self._load_config(config_path) if config_path else {}
        
        # Проверка доступности GPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Create model directories if they don't exist
        try:
            os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
            os.makedirs(TRAINING_DATA_PATH, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directories: {e}")
            raise

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _validate_state(self, state: GameState) -> bool:
        """Validate game state."""
        if not isinstance(state, GameState):
            logger.error(f"Invalid state type: {type(state)}")
            return False
        return True

    def _validate_action(self, action: Action) -> bool:
        """Validate action."""
        if not isinstance(action, Action):
            logger.error(f"Invalid action type: {type(action)}")
            return False
        return True

    def create_player(self, player_type: str, difficulty: int, name: Optional[str] = None) -> AIPlayer:
        """Create a new AI player."""
        try:
            if not isinstance(difficulty, int) or difficulty < 1:
                raise ValueError(f"Invalid difficulty level: {difficulty}")
                
            if player_type == "heuristic":
                player = HeuristicAIPlayer(difficulty, name)
            elif player_type == "neural_net":
                player = NeuralNetAIPlayer(difficulty, name)
            elif player_type == "rl":
                player = ReinforcementLearningAIPlayer(difficulty, name)
            else:
                raise ValueError(f"Unknown player type: {player_type}")
            
            self.players[player.name] = player
            logger.info(f"Created {player_type} player: {player.name}")
            return player
        except Exception as e:
            logger.error(f"Failed to create player: {e}")
            raise

    def get_player(self, name: str) -> Optional[AIPlayer]:
        """Get an AI player by name."""
        return self.players.get(name)

    def remove_player(self, name: str):
        """Remove an AI player."""
        if name in self.players:
            del self.players[name]
            logger.info(f"Removed player: {name}")

    def get_action(self, player_name: str, state: GameState) -> Action:
        """Get the next action for a player."""
        if not self._validate_state(state):
            raise ValueError("Invalid game state")
            
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
            
        try:
            action = player.get_action(state)
            if not self._validate_action(action):
                raise ValueError("Invalid action returned by player")
            return action
        except Exception as e:
            logger.error(f"Failed to get action: {e}")
            raise

    def update(self, player_name: str, state: GameState, action: Action, reward: float, next_state: GameState):
        """Update a player's knowledge."""
        if not self._validate_state(state) or not self._validate_state(next_state):
            raise ValueError("Invalid game state")
            
        if not self._validate_action(action):
            raise ValueError("Invalid action")
            
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
            
        try:
            player.update(state, action, reward, next_state)
            logger.debug(f"Updated player {player_name} with reward {reward}")
        except Exception as e:
            logger.error(f"Failed to update player: {e}")
            raise

    def save_player(self, player_name: str, path: Optional[str] = None):
        """Save a player's state."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        
        if path is None:
            path = os.path.join(MODEL_SAVE_PATH, f"{player_name}.pt")
        
        try:
            player.save(path)
            logger.info(f"Saved player {player_name} to {path}")
        except Exception as e:
            logger.error(f"Failed to save player: {e}")
            raise

    def load_player(self, player_name: str, path: Optional[str] = None):
        """Load a player's state."""
        if path is None:
            path = os.path.join(MODEL_SAVE_PATH, f"{player_name}.pt")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        try:
            # Determine player type from file name
            if "heuristic" in path:
                player = HeuristicAIPlayer(1, player_name)
            elif "neural_net" in path:
                player = NeuralNetAIPlayer(1, player_name)
            elif "rl" in path:
                player = ReinforcementLearningAIPlayer(1, player_name)
            else:
                raise ValueError(f"Could not determine player type from path: {path}")
            
            player.load(path)
            self.players[player_name] = player
            logger.info(f"Loaded player {player_name} from {path}")
        except Exception as e:
            logger.error(f"Failed to load player: {e}")
            raise

    def save_training_data(self, path: Optional[str] = None):
        """Save training data to file."""
        if path is None:
            path = os.path.join(TRAINING_DATA_PATH, f"training_data_{int(time.time())}.json")
        
        try:
            with open(path, 'w') as f:
                json.dump(self.training_data, f)
            logger.info(f"Saved training data to {path}")
        except Exception as e:
            logger.error(f"Failed to save training data: {e}")
            raise

    def load_training_data(self, path: str):
        """Load training data from file."""
        try:
            with open(path, 'r') as f:
                self.training_data = json.load(f)
            logger.info(f"Loaded training data from {path}")
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
            raise

    def train_player(self, player_name: str, epochs: int = EPOCHS, batch_size: int = BATCH_SIZE):
        """Train a player using collected training data."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        
        if not isinstance(player, (NeuralNetAIPlayer, ReinforcementLearningAIPlayer)):
            raise ValueError(f"Player type {type(player)} does not support training")
        
        if not self.training_data:
            raise ValueError("No training data available")
        
        try:
            # Convert training data to tensors and move to device
            states = torch.FloatTensor([d[0] for d in self.training_data]).to(self.device)
            actions = torch.LongTensor([d[1] for d in self.training_data]).to(self.device)
            rewards = torch.FloatTensor([d[2] for d in self.training_data]).to(self.device)
            
            # Create data loader
            dataset = torch.utils.data.TensorDataset(states, actions, rewards)
            dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
            # Move model to device
            player.model = player.model.to(self.device)
            
            # Training loop
            optimizer = optim.Adam(player.model.parameters(), lr=LEARNING_RATE)
            criterion = nn.MSELoss()
            
            logger.info(f"Starting training for player {player_name}")
            for epoch in range(epochs):
                total_loss = 0
                for batch_states, batch_actions, batch_rewards in dataloader:
                    optimizer.zero_grad()
                    predictions = player.model(batch_states)
                    loss = criterion(predictions, batch_rewards)
                    loss.backward()
                    optimizer.step()
                    total_loss += loss.item()
                
                avg_loss = total_loss / len(dataloader)
                logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
                
            logger.info(f"Training completed for player {player_name}")
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    def evaluate_player(self, player_name: str, test_data: List[Tuple]) -> float:
        """Evaluate a player's performance on test data."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        
        try:
            total_reward = 0
            for state, action, reward in test_data:
                if not self._validate_state(state) or not self._validate_action(action):
                    logger.warning("Invalid state or action in test data, skipping")
                    continue
                    
                predicted_action = player.get_action(state)
                if predicted_action.action_type == action.action_type:
                    total_reward += reward
            
            avg_reward = total_reward / len(test_data) if test_data else 0.0
            logger.info(f"Player {player_name} evaluation score: {avg_reward:.4f}")
            return avg_reward
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise

def main():
    print("ai_system main entry. Add your AI logic here.") 