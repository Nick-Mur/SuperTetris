"""
AI system implementation.
"""

import os
import json
import time
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
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

class AISystem:
    """Main AI system class that manages AI players and training."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the AI system."""
        self.players: Dict[str, AIPlayer] = {}
        self.training_data: List[Tuple] = []
        self.config = self._load_config(config_path) if config_path else {}
        
        # Create model directories if they don't exist
        os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
        os.makedirs(TRAINING_DATA_PATH, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def create_player(self, player_type: str, difficulty: int, name: Optional[str] = None) -> AIPlayer:
        """Create a new AI player."""
        if player_type == "heuristic":
            player = HeuristicAIPlayer(difficulty, name)
        elif player_type == "neural_net":
            player = NeuralNetAIPlayer(difficulty, name)
        elif player_type == "rl":
            player = ReinforcementLearningAIPlayer(difficulty, name)
        else:
            raise ValueError(f"Unknown player type: {player_type}")
        
        self.players[player.name] = player
        return player

    def get_player(self, name: str) -> Optional[AIPlayer]:
        """Get an AI player by name."""
        return self.players.get(name)

    def remove_player(self, name: str):
        """Remove an AI player."""
        if name in self.players:
            del self.players[name]

    def get_action(self, player_name: str, state: GameState) -> Action:
        """Get the next action for a player."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        return player.get_action(state)

    def update(self, player_name: str, state: GameState, action: Action, reward: float, next_state: GameState):
        """Update a player's knowledge."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        player.update(state, action, reward, next_state)

    def save_player(self, player_name: str, path: Optional[str] = None):
        """Save a player's state."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        
        if path is None:
            path = os.path.join(MODEL_SAVE_PATH, f"{player_name}.pt")
        
        player.save(path)

    def load_player(self, player_name: str, path: Optional[str] = None):
        """Load a player's state."""
        if path is None:
            path = os.path.join(MODEL_SAVE_PATH, f"{player_name}.pt")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
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

    def save_training_data(self, path: Optional[str] = None):
        """Save training data to file."""
        if path is None:
            path = os.path.join(TRAINING_DATA_PATH, f"training_data_{int(time.time())}.json")
        
        with open(path, 'w') as f:
            json.dump(self.training_data, f)

    def load_training_data(self, path: str):
        """Load training data from file."""
        with open(path, 'r') as f:
            self.training_data = json.load(f)

    def train_player(self, player_name: str, epochs: int = EPOCHS, batch_size: int = BATCH_SIZE):
        """Train a player using collected training data."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        
        if not isinstance(player, (NeuralNetAIPlayer, ReinforcementLearningAIPlayer)):
            raise ValueError(f"Player type {type(player)} does not support training")
        
        if not self.training_data:
            raise ValueError("No training data available")
        
        # Convert training data to tensors
        states = torch.FloatTensor([d[0] for d in self.training_data])
        actions = torch.LongTensor([d[1] for d in self.training_data])
        rewards = torch.FloatTensor([d[2] for d in self.training_data])
        
        # Create data loader
        dataset = torch.utils.data.TensorDataset(states, actions, rewards)
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Training loop
        optimizer = optim.Adam(player.model.parameters(), lr=LEARNING_RATE)
        criterion = nn.MSELoss()
        
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
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")

    def evaluate_player(self, player_name: str, test_data: List[Tuple]) -> float:
        """Evaluate a player's performance on test data."""
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"Player not found: {player_name}")
        
        total_reward = 0
        for state, action, reward in test_data:
            predicted_action = player.get_action(state)
            if predicted_action.action_type == action.action_type:
                total_reward += reward
        
        return total_reward / len(test_data) if test_data else 0.0 