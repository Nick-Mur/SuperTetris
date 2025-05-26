#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tetris Towers Game Logic Module

This module implements the core game logic for Tetris Towers, a game combining
elements of Tetris and Tricky Towers. It handles game state, rules, scoring,
and interactions between different game elements.

The module is designed to interface with the C++ physics engine via the Rust server,
providing a high-level API for game mechanics while delegating physics calculations
to the specialized C++ component.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
import json
import uuid
import time
import random
import logging
import threading
import queue
import ctypes
import os
import sys
from enum import Enum, auto
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tetris_towers_logic.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TetrisTowersLogic")

# Game constants
class GameConstants:
    """Constants used throughout the game logic."""
    
    # Board dimensions
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    VISIBLE_BOARD_HEIGHT = 20
    
    # Block dimensions
    BLOCK_SIZE = 30
    
    # Game speed
    INITIAL_FALL_SPEED = 1.0  # blocks per second
    SPEED_INCREASE_FACTOR = 0.05  # increase per level
    MAX_FALL_SPEED = 20.0
    
    # Scoring
    POINTS_SINGLE_LINE = 100
    POINTS_DOUBLE_LINE = 300
    POINTS_TRIPLE_LINE = 500
    POINTS_TETRIS = 800
    POINTS_SOFT_DROP = 1
    POINTS_HARD_DROP = 2
    POINTS_COMBO_MULTIPLIER = 50  # per combo
    
    # Physics
    GRAVITY = 9.8
    BLOCK_DENSITY = 1.0
    BLOCK_FRICTION = 0.3
    BLOCK_RESTITUTION = 0.2  # bounciness
    
    # Game modes
    GAME_MODE_RACE = "race"
    GAME_MODE_PUZZLE = "puzzle"
    GAME_MODE_SURVIVAL = "survival"
    
    # Spell types
    SPELL_TYPE_LIGHT = "light"
    SPELL_TYPE_DARK = "dark"
    
    # Spell effects
    SPELL_EFFECT_STRENGTHEN = "strengthen"
    SPELL_EFFECT_LIGHTEN = "lighten"
    SPELL_EFFECT_MULTIPLY = "multiply"
    SPELL_EFFECT_BRIDGE = "bridge"
    SPELL_EFFECT_DESTABILIZE = "destabilize"
    SPELL_EFFECT_WIND = "wind"
    SPELL_EFFECT_SLIPPERY = "slippery"
    SPELL_EFFECT_GROW = "grow"
    
    # Network
    DEFAULT_PORT = 8080
    DEFAULT_HOST = "localhost"
    
    # AI
    AI_DIFFICULTY_EASY = "easy"
    AI_DIFFICULTY_MEDIUM = "medium"
    AI_DIFFICULTY_HARD = "hard"
    
    # Misc
    MAX_PLAYERS = 4
    MAX_BLOCKS = 1000
    MAX_SPELLS = 10
    SAVE_INTERVAL = 60  # seconds


class BlockType(Enum):
    """Types of Tetris blocks (tetrominoes)."""
    I = auto()  # I-block (long)
    J = auto()  # J-block
    L = auto()  # L-block
    O = auto()  # O-block (square)
    S = auto()  # S-block
    T = auto()  # T-block
    Z = auto()  # Z-block
    SPECIAL = auto()  # Special blocks for Tricky Towers mechanics


class BlockRotation(Enum):
    """Rotation states for blocks."""
    R0 = 0    # 0 degrees (initial state)
    R90 = 90  # 90 degrees clockwise
    R180 = 180  # 180 degrees
    R270 = 270  # 270 degrees clockwise (or 90 counterclockwise)


class GameMode(Enum):
    """Game modes available in Tetris Towers."""
    RACE = auto()     # Race to the top
    PUZZLE = auto()   # Solve puzzles with limited blocks
    SURVIVAL = auto()  # Last player standing


class SpellType(Enum):
    """Types of spells that can be cast during gameplay."""
    LIGHT = auto()  # Helpful spells
    DARK = auto()   # Harmful spells


class GameState(Enum):
    """Possible states of a game."""
    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class PlayerState(Enum):
    """Possible states of a player."""
    WAITING = auto()
    READY = auto()
    PLAYING = auto()
    ELIMINATED = auto()
    VICTORIOUS = auto()


class Direction(Enum):
    """Movement directions for blocks."""
    LEFT = auto()
    RIGHT = auto()
    DOWN = auto()
    UP = auto()  # Rarely used but included for completeness


@dataclass
class Position:
    """2D position with x and y coordinates."""
    x: float
    y: float
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y)
    
    def distance_to(self, other) -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple representation."""
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, tup: Tuple[float, float]) -> 'Position':
        """Create a Position from a tuple."""
        return cls(tup[0], tup[1])


@dataclass
class BlockShape:
    """Represents the shape of a tetromino block."""
    block_type: BlockType
    cells: List[List[bool]]  # 2D grid representing the shape
    width: int
    height: int
    
    @classmethod
    def create(cls, block_type: BlockType) -> 'BlockShape':
        """Factory method to create standard tetromino shapes."""
        if block_type == BlockType.I:
            return cls(
                block_type=BlockType.I,
                cells=[
                    [False, False, False, False],
                    [True, True, True, True],
                    [False, False, False, False],
                    [False, False, False, False]
                ],
                width=4,
                height=4
            )
        elif block_type == BlockType.J:
            return cls(
                block_type=BlockType.J,
                cells=[
                    [True, False, False],
                    [True, True, True],
                    [False, False, False]
                ],
                width=3,
                height=3
            )
        elif block_type == BlockType.L:
            return cls(
                block_type=BlockType.L,
                cells=[
                    [False, False, True],
                    [True, True, True],
                    [False, False, False]
                ],
                width=3,
                height=3
            )
        elif block_type == BlockType.O:
            return cls(
                block_type=BlockType.O,
                cells=[
                    [True, True],
                    [True, True]
                ],
                width=2,
                height=2
            )
        elif block_type == BlockType.S:
            return cls(
                block_type=BlockType.S,
                cells=[
                    [False, True, True],
                    [True, True, False],
                    [False, False, False]
                ],
                width=3,
                height=3
            )
        elif block_type == BlockType.T:
            return cls(
                block_type=BlockType.T,
                cells=[
                    [False, True, False],
                    [True, True, True],
                    [False, False, False]
                ],
                width=3,
                height=3
            )
        elif block_type == BlockType.Z:
            return cls(
                block_type=BlockType.Z,
                cells=[
                    [True, True, False],
                    [False, True, True],
                    [False, False, False]
                ],
                width=3,
                height=3
            )
        elif block_type == BlockType.SPECIAL:
            # Create a random special block for Tricky Towers mechanics
            # This is just an example; actual special blocks would be more varied
            cells = [[False for _ in range(3)] for _ in range(3)]
            # Create a random pattern
            for i in range(3):
                for j in range(3):
                    cells[i][j] = random.random() > 0.5
            
            # Ensure at least one cell is filled
            if not any(any(row) for row in cells):
                cells[1][1] = True
                
            return cls(
                block_type=BlockType.SPECIAL,
                cells=cells,
                width=3,
                height=3
            )
        else:
            raise ValueError(f"Unknown block type: {block_type}")
    
    def rotate(self, rotation: BlockRotation) -> 'BlockShape':
        """Create a new BlockShape with the specified rotation."""
        if rotation == BlockRotation.R0:
            return self
        
        # For O blocks, rotation doesn't change the shape
        if self.block_type == BlockType.O:
            return self
        
        new_cells = []
        
        if rotation == BlockRotation.R90:
            # 90 degrees clockwise
            new_cells = [[False for _ in range(self.height)] for _ in range(self.width)]
            for i in range(self.height):
                for j in range(self.width):
                    new_cells[j][self.height - 1 - i] = self.cells[i][j]
            return BlockShape(self.block_type, new_cells, self.height, self.width)
        
        elif rotation == BlockRotation.R180:
            # 180 degrees
            new_cells = [[False for _ in range(self.width)] for _ in range(self.height)]
            for i in range(self.height):
                for j in range(self.width):
                    new_cells[self.height - 1 - i][self.width - 1 - j] = self.cells[i][j]
            return BlockShape(self.block_type, new_cells, self.width, self.height)
        
        elif rotation == BlockRotation.R270:
            # 270 degrees clockwise (or 90 counterclockwise)
            new_cells = [[False for _ in range(self.height)] for _ in range(self.width)]
            for i in range(self.height):
                for j in range(self.width):
                    new_cells[self.width - 1 - j][i] = self.cells[i][j]
            return BlockShape(self.block_type, new_cells, self.height, self.width)
        
        else:
            raise ValueError(f"Unknown rotation: {rotation}")


@dataclass
class Block:
    """Represents a block in the game with physical properties."""
    id: int
    block_type: BlockType
    shape: BlockShape
    position: Position
    rotation: BlockRotation = BlockRotation.R0
    angle: float = 0.0  # Physical angle in radians
    velocity: Position = field(default_factory=lambda: Position(0, 0))
    angular_velocity: float = 0.0
    density: float = GameConstants.BLOCK_DENSITY
    friction: float = GameConstants.BLOCK_FRICTION
    restitution: float = GameConstants.BLOCK_RESTITUTION
    is_active: bool = True
    is_static: bool = False
    is_placed: bool = False
    player_id: Optional[str] = None
    
    def rotate_clockwise(self) -> None:
        """Rotate the block 90 degrees clockwise."""
        rotations = list(BlockRotation)
        current_idx = rotations.index(self.rotation)
        next_idx = (current_idx + 1) % len(rotations)
        self.rotation = rotations[next_idx]
        self.shape = self.shape.rotate(self.rotation)
    
    def rotate_counterclockwise(self) -> None:
        """Rotate the block 90 degrees counterclockwise."""
        rotations = list(BlockRotation)
        current_idx = rotations.index(self.rotation)
        next_idx = (current_idx - 1) % len(rotations)
        self.rotation = rotations[next_idx]
        self.shape = self.shape.rotate(self.rotation)
    
    def move(self, direction: Direction, distance: float = 1.0) -> None:
        """Move the block in the specified direction."""
        if direction == Direction.LEFT:
            self.position.x -= distance
        elif direction == Direction.RIGHT:
            self.position.x += distance
        elif direction == Direction.DOWN:
            self.position.y += distance
        elif direction == Direction.UP:
            self.position.y -= distance
    
    def apply_force(self, force_x: float, force_y: float) -> None:
        """Apply a force to the block, changing its velocity."""
        self.velocity.x += force_x
        self.velocity.y += force_y
    
    def apply_torque(self, torque: float) -> None:
        """Apply torque to the block, changing its angular velocity."""
        self.angular_velocity += torque
    
    def update_physics(self, dt: float) -> None:
        """Update the block's position and angle based on its velocity and angular velocity."""
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        self.angle += self.angular_velocity * dt
    
    def get_cells(self) -> List[Tuple[int, int]]:
        """Get the list of cells occupied by this block in its current position and rotation."""
        cells = []
        for i in range(self.shape.height):
            for j in range(self.shape.width):
                if self.shape.cells[i][j]:
                    x = int(self.position.x) + j
                    y = int(self.position.y) + i
                    cells.append((x, y))
        return cells
    
    def collides_with(self, other: 'Block') -> bool:
        """Check if this block collides with another block."""
        my_cells = self.get_cells()
        other_cells = other.get_cells()
        
        # Check for any overlapping cells
        return any(cell in other_cells for cell in my_cells)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the block to a dictionary for serialization."""
        return {
            "id": self.id,
            "block_type": self.block_type.name,
            "position": {"x": self.position.x, "y": self.position.y},
            "rotation": self.rotation.value,
            "angle": self.angle,
            "velocity": {"x": self.velocity.x, "y": self.velocity.y},
            "angular_velocity": self.angular_velocity,
            "density": self.density,
            "friction": self.friction,
            "restitution": self.restitution,
            "is_active": self.is_active,
            "is_static": self.is_static,
            "is_placed": self.is_placed,
            "player_id": self.player_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Create a Block from a dictionary."""
        block_type = BlockType[data["block_type"]]
        shape = BlockShape.create(block_type)
        rotation = BlockRotation(data["rotation"])
        
        # Apply the rotation to the shape
        if rotation != BlockRotation.R0:
            shape = shape.rotate(rotation)
        
        return cls(
            id=data["id"],
            block_type=block_type,
            shape=shape,
            position=Position(data["position"]["x"], data["position"]["y"]),
            rotation=rotation,
            angle=data["angle"],
            velocity=Position(data["velocity"]["x"], data["velocity"]["y"]),
            angular_velocity=data["angular_velocity"],
            density=data["density"],
            friction=data["friction"],
            restitution=data["restitution"],
            is_active=data["is_active"],
            is_static=data["is_static"],
            is_placed=data["is_placed"],
            player_id=data["player_id"]
        )


@dataclass
class Spell:
    """Represents a spell that can be cast during gameplay."""
    id: str
    name: str
    spell_type: SpellType
    effect: str
    duration: float  # in seconds
    strength: float  # effect magnitude
    target_type: str  # "self", "opponent", "all"
    cooldown: float  # in seconds
    mana_cost: int
    description: str
    icon_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the spell to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "spell_type": self.spell_type.name,
            "effect": self.effect,
            "duration": self.duration,
            "strength": self.strength,
            "target_type": self.target_type,
            "cooldown": self.cooldown,
            "mana_cost": self.mana_cost,
            "description": self.description,
            "icon_path": self.icon_path
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Spell':
        """Create a Spell from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            spell_type=SpellType[data["spell_type"]],
            effect=data["effect"],
            duration=data["duration"],
            strength=data["strength"],
            target_type=data["target_type"],
            cooldown=data["cooldown"],
            mana_cost=data["mana_cost"],
            description=data["description"],
            icon_path=data["icon_path"]
        )


@dataclass
class ActiveSpell:
    """Represents an active spell affecting the game."""
    spell: Spell
    caster_id: str
    target_id: str
    start_time: float
    end_time: float
    is_active: bool = True
    
    def is_expired(self, current_time: float) -> bool:
        """Check if the spell has expired."""
        return current_time >= self.end_time
    
    def remaining_time(self, current_time: float) -> float:
        """Get the remaining time for this spell."""
        if self.is_expired(current_time):
            return 0.0
        return self.end_time - current_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the active spell to a dictionary for serialization."""
        return {
            "spell": self.spell.to_dict(),
            "caster_id": self.caster_id,
            "target_id": self.target_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActiveSpell':
        """Create an ActiveSpell from a dictionary."""
        return cls(
            spell=Spell.from_dict(data["spell"]),
            caster_id=data["caster_id"],
            target_id=data["target_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            is_active=data["is_active"]
        )


@dataclass
class Player:
    """Represents a player in the game."""
    id: str
    name: str
    state: PlayerState = PlayerState.WAITING
    score: int = 0
    level: int = 1
    lines_cleared: int = 0
    combo_count: int = 0
    mana: int = 0
    max_mana: int = 100
    spells: List[Spell] = field(default_factory=list)
    active_spells: List[ActiveSpell] = field(default_factory=list)
    current_block: Optional[Block] = None
    next_blocks: List[Block] = field(default_factory=list)
    blocks_placed: int = 0
    is_ai: bool = False
    ai_difficulty: Optional[str] = None
    last_action_time: float = field(default_factory=time.time)
    
    def add_score(self, points: int) -> None:
        """Add points to the player's score."""
        self.score += points
    
    def add_lines(self, lines: int) -> None:
        """Add cleared lines to the player's count and update level."""
        self.lines_cleared += lines
        
        # Update level based on lines cleared (every 10 lines)
        new_level = (self.lines_cleared // 10) + 1
        if new_level > self.level:
            self.level = new_level
    
    def add_mana(self, amount: int) -> None:
        """Add mana to the player's pool."""
        self.mana = min(self.mana + amount, self.max_mana)
    
    def use_mana(self, amount: int) -> bool:
        """Use mana if available."""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False
    
    def add_spell(self, spell: Spell) -> None:
        """Add a spell to the player's collection."""
        self.spells.append(spell)
    
    def cast_spell(self, spell_id: str, target_id: str, current_time: float) -> Optional[ActiveSpell]:
        """Cast a spell if the player has it and enough mana."""
        spell = next((s for s in self.spells if s.id == spell_id), None)
        if not spell:
            return None
        
        if not self.use_mana(spell.mana_cost):
            return None
        
        active_spell = ActiveSpell(
            spell=spell,
            caster_id=self.id,
            target_id=target_id,
            start_time=current_time,
            end_time=current_time + spell.duration
        )
        
        self.active_spells.append(active_spell)
        return active_spell
    
    def update_active_spells(self, current_time: float) -> None:
        """Update the status of active spells and remove expired ones."""
        self.active_spells = [
            spell for spell in self.active_spells
            if not spell.is_expired(current_time)
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the player to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.name,
            "score": self.score,
            "level": self.level,
            "lines_cleared": self.lines_cleared,
            "combo_count": self.combo_count,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "spells": [spell.to_dict() for spell in self.spells],
            "active_spells": [spell.to_dict() for spell in self.active_spells],
            "current_block": self.current_block.to_dict() if self.current_block else None,
            "next_blocks": [block.to_dict() for block in self.next_blocks],
            "blocks_placed": self.blocks_placed,
            "is_ai": self.is_ai,
            "ai_difficulty": self.ai_difficulty,
            "last_action_time": self.last_action_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create a Player from a dictionary."""
        player = cls(
            id=data["id"],
            name=data["name"],
            state=PlayerState[data["state"]],
            score=data["score"],
            level=data["level"],
            lines_cleared=data["lines_cleared"],
            combo_count=data["combo_count"],
            mana=data["mana"],
            max_mana=data["max_mana"],
            spells=[Spell.from_dict(spell_data) for spell_data in data["spells"]],
            active_spells=[ActiveSpell.from_dict(spell_data) for spell_data in data["active_spells"]],
            blocks_placed=data["blocks_placed"],
            is_ai=data["is_ai"],
            ai_difficulty=data["ai_difficulty"],
            last_action_time=data["last_action_time"]
        )
        
        if data["current_block"]:
            player.current_block = Block.from_dict(data["current_block"])
        
        player.next_blocks = [Block.from_dict(block_data) for block_data in data["next_blocks"]]
        
        return player


@dataclass
class GameBoard:
    """Represents the game board where blocks are placed."""
    width: int
    height: int
    cells: List[List[Optional[int]]]  # Grid of block IDs (None for empty)
    blocks: Dict[int, Block] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the board with empty cells."""
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is within the board boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_cell_empty(self, x: int, y: int) -> bool:
        """Check if a cell is empty."""
        if not self.is_valid_position(x, y):
            return False
        return self.cells[y][x] is None
    
    def can_place_block(self, block: Block) -> bool:
        """Check if a block can be placed at its current position."""
        for cell_x, cell_y in block.get_cells():
            if not self.is_valid_position(cell_x, cell_y) or not self.is_cell_empty(cell_x, cell_y):
                return False
        return True
    
    def place_block(self, block: Block) -> bool:
        """Place a block on the board."""
        if not self.can_place_block(block):
            return False
        
        for cell_x, cell_y in block.get_cells():
            self.cells[cell_y][cell_x] = block.id
        
        self.blocks[block.id] = block
        block.is_placed = True
        return True
    
    def remove_block(self, block_id: int) -> bool:
        """Remove a block from the board."""
        if block_id not in self.blocks:
            return False
        
        block = self.blocks[block_id]
        
        for cell_x, cell_y in block.get_cells():
            if self.is_valid_position(cell_x, cell_y) and self.cells[cell_y][cell_x] == block_id:
                self.cells[cell_y][cell_x] = None
        
        del self.blocks[block_id]
        return True
    
    def check_lines(self) -> List[int]:
        """Check for completed lines and return their indices."""
        completed_lines = []
        
        for y in range(self.height):
            if all(self.cells[y][x] is not None for x in range(self.width)):
                completed_lines.append(y)
        
        return completed_lines
    
    def clear_lines(self, lines: List[int]) -> int:
        """Clear the specified lines and return the number of lines cleared."""
        if not lines:
            return 0
        
        # Sort lines in descending order to avoid shifting issues
        lines.sort(reverse=True)
        
        for line in lines:
            # Remove blocks in this line
            for x in range(self.width):
                block_id = self.cells[line][x]
                if block_id is not None:
                    self.remove_block(block_id)
            
            # Shift all lines above this one down
            for y in range(line, 0, -1):
                for x in range(self.width):
                    self.cells[y][x] = self.cells[y-1][x]
            
            # Clear the top line
            for x in range(self.width):
                self.cells[0][x] = None
        
        return len(lines)
    
    def get_highest_block_position(self) -> int:
        """Get the y-coordinate of the highest block on the board."""
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] is not None:
                    return y
        return self.height
    
    def is_game_over(self) -> bool:
        """Check if the game is over (blocks stacked to the top)."""
        # If there are blocks in the top row, the game is over
        return any(self.cells[0][x] is not None for x in range(self.width))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the game board to a dictionary for serialization."""
        return {
            "width": self.width,
            "height": self.height,
            "cells": self.cells,
            "blocks": {str(block_id): block.to_dict() for block_id, block in self.blocks.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameBoard':
        """Create a GameBoard from a dictionary."""
        board = cls(
            width=data["width"],
            height=data["height"]
        )
        
        board.cells = data["cells"]
        
        for block_id_str, block_data in data["blocks"].items():
            block_id = int(block_id_str)
            board.blocks[block_id] = Block.from_dict(block_data)
        
        return board


class SpellFactory:
    """Factory for creating spells."""
    
    @staticmethod
    def create_light_spells() -> List[Spell]:
        """Create a list of light (helpful) spells."""
        return [
            Spell(
                id=str(uuid.uuid4()),
                name="Strengthen",
                spell_type=SpellType.LIGHT,
                effect=GameConstants.SPELL_EFFECT_STRENGTHEN,
                duration=15.0,
                strength=2.0,
                target_type="self",
                cooldown=30.0,
                mana_cost=30,
                description="Strengthens your blocks, making them more stable.",
                icon_path="assets/spells/strengthen.png"
            ),
            Spell(
                id=str(uuid.uuid4()),
                name="Lighten",
                spell_type=SpellType.LIGHT,
                effect=GameConstants.SPELL_EFFECT_LIGHTEN,
                duration=10.0,
                strength=0.5,
                target_type="self",
                cooldown=25.0,
                mana_cost=25,
                description="Makes your blocks lighter, reducing their impact when falling.",
                icon_path="assets/spells/lighten.png"
            ),
            Spell(
                id=str(uuid.uuid4()),
                name="Multiply",
                spell_type=SpellType.LIGHT,
                effect=GameConstants.SPELL_EFFECT_MULTIPLY,
                duration=5.0,
                strength=2.0,
                target_type="self",
                cooldown=60.0,
                mana_cost=50,
                description="Doubles the points you earn for a short time.",
                icon_path="assets/spells/multiply.png"
            ),
            Spell(
                id=str(uuid.uuid4()),
                name="Bridge",
                spell_type=SpellType.LIGHT,
                effect=GameConstants.SPELL_EFFECT_BRIDGE,
                duration=0.0,  # Instant effect
                strength=1.0,
                target_type="self",
                cooldown=45.0,
                mana_cost=40,
                description="Creates a horizontal bridge to fill gaps in your tower.",
                icon_path="assets/spells/bridge.png"
            )
        ]
    
    @staticmethod
    def create_dark_spells() -> List[Spell]:
        """Create a list of dark (harmful) spells."""
        return [
            Spell(
                id=str(uuid.uuid4()),
                name="Destabilize",
                spell_type=SpellType.DARK,
                effect=GameConstants.SPELL_EFFECT_DESTABILIZE,
                duration=10.0,
                strength=0.5,
                target_type="opponent",
                cooldown=35.0,
                mana_cost=35,
                description="Destabilizes your opponent's tower, making it more likely to collapse.",
                icon_path="assets/spells/destabilize.png"
            ),
            Spell(
                id=str(uuid.uuid4()),
                name="Wind Gust",
                spell_type=SpellType.DARK,
                effect=GameConstants.SPELL_EFFECT_WIND,
                duration=5.0,
                strength=3.0,
                target_type="opponent",
                cooldown=40.0,
                mana_cost=40,
                description="Creates a gust of wind that pushes your opponent's blocks.",
                icon_path="assets/spells/wind.png"
            ),
            Spell(
                id=str(uuid.uuid4()),
                name="Slippery",
                spell_type=SpellType.DARK,
                effect=GameConstants.SPELL_EFFECT_SLIPPERY,
                duration=12.0,
                strength=0.8,
                target_type="opponent",
                cooldown=30.0,
                mana_cost=30,
                description="Makes your opponent's blocks slippery, reducing friction.",
                icon_path="assets/spells/slippery.png"
            ),
            Spell(
                id=str(uuid.uuid4()),
                name="Grow",
                spell_type=SpellType.DARK,
                effect=GameConstants.SPELL_EFFECT_GROW,
                duration=8.0,
                strength=1.5,
                target_type="opponent",
                cooldown=50.0,
                mana_cost=45,
                description="Makes your opponent's blocks grow larger, making them harder to place.",
                icon_path="assets/spells/grow.png"
            )
        ]
    
    @staticmethod
    def create_all_spells() -> List[Spell]:
        """Create all available spells."""
        return SpellFactory.create_light_spells() + SpellFactory.create_dark_spells()


class BlockFactory:
    """Factory for creating blocks."""
    
    _next_block_id = 1
    
    @classmethod
    def create_block(cls, block_type: Optional[BlockType] = None, player_id: Optional[str] = None) -> Block:
        """Create a new block of the specified type."""
        if block_type is None:
            # Randomly select a block type, with SPECIAL being less common
            weights = [1, 1, 1, 1, 1, 1, 1, 0.3]  # Lower weight for SPECIAL
            block_types = list(BlockType)
            block_type = random.choices(block_types, weights=weights, k=1)[0]
        
        shape = BlockShape.create(block_type)
        
        block = Block(
            id=cls._next_block_id,
            block_type=block_type,
            shape=shape,
            position=Position(0, 0),
            player_id=player_id
        )
        
        cls._next_block_id += 1
        return block
    
    @classmethod
    def create_next_blocks(cls, count: int, player_id: Optional[str] = None) -> List[Block]:
        """Create a list of upcoming blocks."""
        return [cls.create_block(player_id=player_id) for _ in range(count)]
    
    @classmethod
    def reset_block_id_counter(cls) -> None:
        """Reset the block ID counter."""
        cls._next_block_id = 1


class PhysicsEngine:
    """Interface to the C++ physics engine via FFI."""
    
    def __init__(self):
        """Initialize the physics engine."""
        self.lib = None
        self.engine_ptr = None
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize the physics engine library."""
        try:
            # Try to load the shared library
            lib_path = os.path.join(os.path.dirname(__file__), "../cpp_physics/build/libphysics_engine.so")
            self.lib = ctypes.CDLL(lib_path)
            
            # Define the Vec2 structure for FFI
            class Vec2(ctypes.Structure):
                _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]
            
            # Define the BlockInfo structure for FFI
            class BlockInfo(ctypes.Structure):
                _fields_ = [
                    ("id", ctypes.c_int),
                    ("position", Vec2),
                    ("angle", ctypes.c_float),
                    ("linear_velocity", Vec2),
                    ("angular_velocity", ctypes.c_float),
                    ("width", ctypes.c_float),
                    ("height", ctypes.c_float),
                    ("is_static", ctypes.c_bool),
                    ("is_active", ctypes.c_bool)
                ]
            
            # Define the CollisionInfo structure for FFI
            class CollisionInfo(ctypes.Structure):
                _fields_ = [
                    ("block_a_id", ctypes.c_int),
                    ("block_b_id", ctypes.c_int),
                    ("point", Vec2),
                    ("normal", Vec2),
                    ("impulse", ctypes.c_float)
                ]
            
            # Store the structure types
            self.Vec2 = Vec2
            self.BlockInfo = BlockInfo
            self.CollisionInfo = CollisionInfo
            
            # Set up function prototypes
            self.lib.physics_engine_create.restype = ctypes.c_void_p
            self.lib.physics_engine_destroy.argtypes = [ctypes.c_void_p]
            self.lib.physics_engine_step.argtypes = [ctypes.c_void_p, ctypes.c_float]
            self.lib.physics_engine_set_gravity.argtypes = [ctypes.c_void_p, Vec2]
            self.lib.physics_engine_get_gravity.argtypes = [ctypes.c_void_p]
            self.lib.physics_engine_get_gravity.restype = Vec2
            
            # Create the physics engine instance
            self.engine_ptr = self.lib.physics_engine_create()
            
            # Set default gravity
            gravity = Vec2(0.0, GameConstants.GRAVITY)
            self.lib.physics_engine_set_gravity(self.engine_ptr, gravity)
            
            logger.info("Physics engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize physics engine: {e}")
            # Fall back to a simple physics simulation if the C++ library can't be loaded
            self.lib = None
            self.engine_ptr = None
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if self.lib and self.engine_ptr:
            self.lib.physics_engine_destroy(self.engine_ptr)
    
    def step(self, dt: float) -> None:
        """Advance the physics simulation by the specified time step."""
        if self.lib and self.engine_ptr:
            self.lib.physics_engine_step(self.engine_ptr, ctypes.c_float(dt))
        else:
            # Simple fallback physics if the C++ library isn't available
            logger.warning("Using fallback physics simulation")
    
    def create_block(self, block: Block) -> int:
        """Create a block in the physics engine."""
        if self.lib and self.engine_ptr:
            position = self.Vec2(block.position.x, block.position.y)
            block_id = self.lib.physics_engine_create_block(
                self.engine_ptr,
                position,
                ctypes.c_float(block.shape.width),
                ctypes.c_float(block.shape.height),
                ctypes.c_float(block.angle),
                ctypes.c_float(block.density),
                ctypes.c_float(block.friction),
                ctypes.c_float(block.restitution),
                block.is_static
            )
            return block_id
        else:
            # Return the block's ID if the C++ library isn't available
            return block.id
    
    def remove_block(self, block_id: int) -> bool:
        """Remove a block from the physics engine."""
        if self.lib and self.engine_ptr:
            return bool(self.lib.physics_engine_remove_block(self.engine_ptr, block_id))
        return True
    
    def get_block_info(self, block_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a block from the physics engine."""
        if self.lib and self.engine_ptr:
            info = self.BlockInfo()
            if self.lib.physics_engine_get_block_info(self.engine_ptr, block_id, ctypes.byref(info)):
                return {
                    "id": info.id,
                    "position": {"x": info.position.x, "y": info.position.y},
                    "angle": info.angle,
                    "linear_velocity": {"x": info.linear_velocity.x, "y": info.linear_velocity.y},
                    "angular_velocity": info.angular_velocity,
                    "width": info.width,
                    "height": info.height,
                    "is_static": info.is_static,
                    "is_active": info.is_active
                }
        return None
    
    def update_block(self, block: Block) -> None:
        """Update a block's properties in the physics engine."""
        if self.lib and self.engine_ptr:
            position = self.Vec2(block.position.x, block.position.y)
            velocity = self.Vec2(block.velocity.x, block.velocity.y)
            
            self.lib.physics_engine_set_block_position(self.engine_ptr, block.id, position)
            self.lib.physics_engine_set_block_angle(self.engine_ptr, block.id, ctypes.c_float(block.angle))
            self.lib.physics_engine_set_block_linear_velocity(self.engine_ptr, block.id, velocity)
            self.lib.physics_engine_set_block_angular_velocity(self.engine_ptr, block.id, ctypes.c_float(block.angular_velocity))
            self.lib.physics_engine_set_block_active(self.engine_ptr, block.id, block.is_active)
            self.lib.physics_engine_set_block_static(self.engine_ptr, block.id, block.is_static)
    
    def apply_force(self, block_id: int, force_x: float, force_y: float, point_x: float, point_y: float) -> bool:
        """Apply a force to a block at the specified point."""
        if self.lib and self.engine_ptr:
            force = self.Vec2(force_x, force_y)
            point = self.Vec2(point_x, point_y)
            return bool(self.lib.physics_engine_apply_force(self.engine_ptr, block_id, force, point))
        return False
    
    def apply_torque(self, block_id: int, torque: float) -> bool:
        """Apply torque to a block."""
        if self.lib and self.engine_ptr:
            return bool(self.lib.physics_engine_apply_torque(self.engine_ptr, block_id, ctypes.c_float(torque)))
        return False
    
    def check_collision(self, block_a_id: int, block_b_id: int) -> bool:
        """Check if two blocks are colliding."""
        if self.lib and self.engine_ptr:
            return bool(self.lib.physics_engine_check_collision(self.engine_ptr, block_a_id, block_b_id))
        return False
    
    def get_collisions(self) -> List[Dict[str, Any]]:
        """Get all current collisions."""
        if self.lib and self.engine_ptr:
            count = self.lib.physics_engine_get_collision_count(self.engine_ptr)
            if count == 0:
                return []
            
            # Create a buffer to hold the collision information
            collisions_array = (self.CollisionInfo * count)()
            actual_count = self.lib.physics_engine_get_collisions(
                self.engine_ptr,
                ctypes.cast(collisions_array, ctypes.POINTER(self.CollisionInfo)),
                count
            )
            
            # Convert the collision information to dictionaries
            collisions = []
            for i in range(actual_count):
                collision = collisions_array[i]
                collisions.append({
                    "block_a_id": collision.block_a_id,
                    "block_b_id": collision.block_b_id,
                    "point": {"x": collision.point.x, "y": collision.point.y},
                    "normal": {"x": collision.normal.x, "y": collision.normal.y},
                    "impulse": collision.impulse
                })
            
            return collisions
        
        return []


class GameManager:
    """Manages the game state and logic."""
    
    def __init__(self, game_mode: GameMode = GameMode.SURVIVAL):
        """Initialize the game manager."""
        self.game_id = str(uuid.uuid4())
        self.game_mode = game_mode
        self.game_state = GameState.INITIALIZING
        self.players: Dict[str, Player] = {}
        self.boards: Dict[str, GameBoard] = {}
        self.physics_engine = PhysicsEngine()
        self.current_time = time.time()
        self.start_time = 0.0
        self.last_update_time = 0.0
        self.active_spells: List[ActiveSpell] = []
        self.next_block_queue: Dict[str, List[Block]] = {}
        self.block_fall_speed = GameConstants.INITIAL_FALL_SPEED
        self.gravity = GameConstants.GRAVITY
        self.save_timer = 0.0
        self.event_queue = queue.Queue()
        self.lock = threading.RLock()
    
    def initialize_game(self) -> None:
        """Initialize the game with default settings."""
        with self.lock:
            self.game_state = GameState.INITIALIZING
            self.current_time = time.time()
            self.start_time = self.current_time
            self.last_update_time = self.current_time
            
            # Reset block ID counter
            BlockFactory.reset_block_id_counter()
            
            # Initialize physics engine
            self.physics_engine = PhysicsEngine()
            
            # Clear existing data
            self.players.clear()
            self.boards.clear()
            self.active_spells.clear()
            self.next_block_queue.clear()
            
            # Set initial game parameters
            self.block_fall_speed = GameConstants.INITIAL_FALL_SPEED
            self.gravity = GameConstants.GRAVITY
            self.save_timer = 0.0
            
            self.game_state = GameState.READY
    
    def add_player(self, name: str, is_ai: bool = False, ai_difficulty: Optional[str] = None) -> str:
        """Add a player to the game and return their ID."""
        with self.lock:
            if len(self.players) >= GameConstants.MAX_PLAYERS:
                raise ValueError("Maximum number of players reached")
            
            player_id = str(uuid.uuid4())
            
            # Create the player
            player = Player(
                id=player_id,
                name=name,
                is_ai=is_ai,
                ai_difficulty=ai_difficulty
            )
            
            # Add some initial spells
            if random.random() < 0.5:
                # Give light spells
                player.spells = SpellFactory.create_light_spells()
            else:
                # Give dark spells
                player.spells = SpellFactory.create_dark_spells()
            
            # Create a game board for this player
            board = GameBoard(
                width=GameConstants.BOARD_WIDTH,
                height=GameConstants.BOARD_HEIGHT
            )
            
            # Generate initial blocks
            next_blocks = BlockFactory.create_next_blocks(3, player_id)
            player.next_blocks = next_blocks
            
            # Store the player and board
            self.players[player_id] = player
            self.boards[player_id] = board
            
            return player_id
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        with self.lock:
            if player_id not in self.players:
                return False
            
            # Remove the player and their board
            del self.players[player_id]
            
            if player_id in self.boards:
                del self.boards[player_id]
            
            if player_id in self.next_block_queue:
                del self.next_block_queue[player_id]
            
            # Remove any active spells cast by or targeting this player
            self.active_spells = [
                spell for spell in self.active_spells
                if spell.caster_id != player_id and spell.target_id != player_id
            ]
            
            return True
    
    def start_game(self) -> bool:
        """Start the game if all players are ready."""
        with self.lock:
            if self.game_state != GameState.READY:
                return False
            
            if not self.players:
                return False
            
            # Check if all players are ready
            if not all(player.state == PlayerState.READY for player in self.players.values()):
                return False
            
            # Set game state to running
            self.game_state = GameState.RUNNING
            self.current_time = time.time()
            self.start_time = self.current_time
            self.last_update_time = self.current_time
            
            # Set all players to playing state
            for player in self.players.values():
                player.state = PlayerState.PLAYING
                
                # Give each player their first block
                self._give_next_block(player.id)
            
            return True
    
    def pause_game(self) -> bool:
        """Pause the game."""
        with self.lock:
            if self.game_state != GameState.RUNNING:
                return False
            
            self.game_state = GameState.PAUSED
            return True
    
    def resume_game(self) -> bool:
        """Resume the game."""
        with self.lock:
            if self.game_state != GameState.PAUSED:
                return False
            
            self.game_state = GameState.RUNNING
            self.current_time = time.time()
            self.last_update_time = self.current_time
            return True
    
    def end_game(self) -> None:
        """End the game and determine the winner."""
        with self.lock:
            if self.game_state not in (GameState.RUNNING, GameState.PAUSED):
                return
            
            # Determine the winner based on game mode
            if self.game_mode == GameMode.RACE:
                # Winner is the player who reached the top first
                winner_id = None
                highest_position = float('inf')
                
                for player_id, board in self.boards.items():
                    position = board.get_highest_block_position()
                    if position < highest_position:
                        highest_position = position
                        winner_id = player_id
                
                if winner_id:
                    self.players[winner_id].state = PlayerState.VICTORIOUS
            
            elif self.game_mode == GameMode.SURVIVAL:
                # Winner is the last player standing
                active_players = [
                    player_id for player_id, player in self.players.items()
                    if player.state == PlayerState.PLAYING
                ]
                
                if len(active_players) == 1:
                    self.players[active_players[0]].state = PlayerState.VICTORIOUS
            
            elif self.game_mode == GameMode.PUZZLE:
                # Winner is the player who completed the puzzle with the fewest blocks
                winner_id = None
                min_blocks = float('inf')
                
                for player_id, player in self.players.items():
                    if player.state == PlayerState.PLAYING and player.blocks_placed < min_blocks:
                        min_blocks = player.blocks_placed
                        winner_id = player_id
                
                if winner_id:
                    self.players[winner_id].state = PlayerState.VICTORIOUS
            
            # Set game state to game over
            self.game_state = GameState.GAME_OVER
    
    def update(self) -> None:
        """Update the game state."""
        with self.lock:
            if self.game_state != GameState.RUNNING:
                return
            
            # Update current time
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.current_time = current_time
            self.last_update_time = current_time
            
            # Update physics
            self.physics_engine.step(dt)
            
            # Update active spells
            self._update_active_spells()
            
            # Update players
            for player_id, player in list(self.players.items()):
                if player.state != PlayerState.PLAYING:
                    continue
                
                # Update player's active spells
                player.update_active_spells(self.current_time)
                
                # Update current block position
                if player.current_block:
                    self._update_block_position(player_id, dt)
                
                # Check for game over conditions
                board = self.boards.get(player_id)
                if board and board.is_game_over():
                    player.state = PlayerState.ELIMINATED
                    
                    # Check if this was the last active player
                    active_players = [
                        p for p in self.players.values()
                        if p.state == PlayerState.PLAYING
                    ]
                    
                    if not active_players:
                        self.end_game()
                
                # Handle AI players
                if player.is_ai:
                    self._handle_ai_player(player_id, dt)
            
            # Check for victory conditions based on game mode
            self._check_victory_conditions()
            
            # Periodically save game state
            self.save_timer += dt
            if self.save_timer >= GameConstants.SAVE_INTERVAL:
                self.save_timer = 0
                self._save_game_state()
    
    def _update_active_spells(self) -> None:
        """Update all active spells and remove expired ones."""
        # Filter out expired spells
        self.active_spells = [
            spell for spell in self.active_spells
            if not spell.is_expired(self.current_time)
        ]
        
        # Apply spell effects
        for spell in self.active_spells:
            self._apply_spell_effect(spell)
    
    def _apply_spell_effect(self, active_spell: ActiveSpell) -> None:
        """Apply the effect of an active spell."""
        spell = active_spell.spell
        target_id = active_spell.target_id
        
        # Skip if the target player doesn't exist
        if target_id not in self.players:
            return
        
        # Apply different effects based on the spell type
        if spell.effect == GameConstants.SPELL_EFFECT_STRENGTHEN:
            # Increase block density and friction
            if self.players[target_id].current_block:
                block = self.players[target_id].current_block
                block.density *= spell.strength
                block.friction *= spell.strength
                self.physics_engine.update_block(block)
        
        elif spell.effect == GameConstants.SPELL_EFFECT_LIGHTEN:
            # Decrease block density
            if self.players[target_id].current_block:
                block = self.players[target_id].current_block
                block.density *= spell.strength  # strength < 1 for lightening
                self.physics_engine.update_block(block)
        
        elif spell.effect == GameConstants.SPELL_EFFECT_MULTIPLY:
            # This is handled when scoring points
            pass
        
        elif spell.effect == GameConstants.SPELL_EFFECT_BRIDGE:
            # Create a horizontal bridge
            board = self.boards.get(target_id)
            if board and self.players[target_id].current_block:
                current_block = self.players[target_id].current_block
                x = int(current_block.position.x)
                y = int(current_block.position.y)
                
                # Find the nearest gap
                gap_start = None
                gap_end = None
                
                # Look left for the start of a gap
                for i in range(x, 0, -1):
                    if not board.is_cell_empty(i, y):
                        gap_start = i + 1
                        break
                
                # Look right for the end of a gap
                for i in range(x, board.width):
                    if not board.is_cell_empty(i, y):
                        gap_end = i - 1
                        break
                
                if gap_start is not None and gap_end is not None and gap_start <= gap_end:
                    # Create blocks to fill the gap
                    for i in range(gap_start, gap_end + 1):
                        bridge_block = BlockFactory.create_block(BlockType.SPECIAL, target_id)
                        bridge_block.position = Position(i, y)
                        bridge_block.is_static = True
                        
                        # Place the block on the board
                        board.place_block(bridge_block)
                        
                        # Add to physics engine
                        self.physics_engine.create_block(bridge_block)
        
        elif spell.effect == GameConstants.SPELL_EFFECT_DESTABILIZE:
            # Decrease friction and increase angular velocity
            board = self.boards.get(target_id)
            if board:
                for block in board.blocks.values():
                    block.friction *= spell.strength  # strength < 1 for destabilizing
                    block.angular_velocity += random.uniform(-2.0, 2.0)
                    self.physics_engine.update_block(block)
        
        elif spell.effect == GameConstants.SPELL_EFFECT_WIND:
            # Apply a horizontal force to all blocks
            board = self.boards.get(target_id)
            if board:
                wind_direction = 1 if random.random() > 0.5 else -1
                wind_force = spell.strength * wind_direction
                
                for block in board.blocks.values():
                    if not block.is_static:
                        self.physics_engine.apply_force(
                            block.id,
                            wind_force,
                            0.0,
                            block.position.x,
                            block.position.y
                        )
        
        elif spell.effect == GameConstants.SPELL_EFFECT_SLIPPERY:
            # Decrease friction
            board = self.boards.get(target_id)
            if board:
                for block in board.blocks.values():
                    block.friction *= spell.strength  # strength < 1 for slippery
                    self.physics_engine.update_block(block)
        
        elif spell.effect == GameConstants.SPELL_EFFECT_GROW:
            # Increase block size
            if self.players[target_id].current_block:
                block = self.players[target_id].current_block
                # This would require more complex handling in a real implementation
                # For now, we just make it harder to place by increasing density
                block.density *= spell.strength
                self.physics_engine.update_block(block)
    
    def _update_block_position(self, player_id: str, dt: float) -> None:
        """Update the position of a player's current block."""
        player = self.players.get(player_id)
        if not player or not player.current_block:
            return
        
        board = self.boards.get(player_id)
        if not board:
            return
        
        block = player.current_block
        
        # Calculate fall distance based on speed and time
        fall_speed = self.block_fall_speed * player.level * GameConstants.SPEED_INCREASE_FACTOR
        fall_distance = fall_speed * dt
        
        # Move the block down
        old_position = Position(block.position.x, block.position.y)
        block.position.y += fall_distance
        
        # Check if the block can be placed at the new position
        if not board.can_place_block(block):
            # Revert to the old position
            block.position = old_position
            
            # Try to place the block
            if board.place_block(block):
                player.blocks_placed += 1
                
                # Add the block to the physics engine
                self.physics_engine.create_block(block)
                
                # Check for completed lines
                completed_lines = board.check_lines()
                if completed_lines:
                    lines_cleared = board.clear_lines(completed_lines)
                    
                    # Update player stats
                    player.add_lines(lines_cleared)
                    
                    # Calculate score
                    score = self._calculate_score(lines_cleared, player.combo_count)
                    
                    # Apply score multiplier from spells
                    for spell in player.active_spells:
                        if spell.spell.effect == GameConstants.SPELL_EFFECT_MULTIPLY:
                            score = int(score * spell.spell.strength)
                    
                    player.add_score(score)
                    
                    # Update combo count
                    player.combo_count += 1
                else:
                    # Reset combo count
                    player.combo_count = 0
                
                # Give the player their next block
                self._give_next_block(player_id)
    
    def _give_next_block(self, player_id: str) -> None:
        """Give the player their next block."""
        player = self.players.get(player_id)
        if not player:
            return
        
        # Take the next block from the queue
        if player.next_blocks:
            player.current_block = player.next_blocks.pop(0)
            
            # Position the block at the top center of the board
            board = self.boards.get(player_id)
            if board:
                player.current_block.position = Position(
                    board.width // 2 - player.current_block.shape.width // 2,
                    0
                )
        
        # Generate a new block for the queue
        new_block = BlockFactory.create_block(player_id=player_id)
        player.next_blocks.append(new_block)
    
    def _calculate_score(self, lines_cleared: int, combo_count: int) -> int:
        """Calculate the score for clearing lines."""
        base_score = 0
        
        if lines_cleared == 1:
            base_score = GameConstants.POINTS_SINGLE_LINE
        elif lines_cleared == 2:
            base_score = GameConstants.POINTS_DOUBLE_LINE
        elif lines_cleared == 3:
            base_score = GameConstants.POINTS_TRIPLE_LINE
        elif lines_cleared >= 4:
            base_score = GameConstants.POINTS_TETRIS
        
        # Add combo bonus
        combo_bonus = combo_count * GameConstants.POINTS_COMBO_MULTIPLIER
        
        return base_score + combo_bonus
    
    def _check_victory_conditions(self) -> None:
        """Check for victory conditions based on the game mode."""
        if self.game_state != GameState.RUNNING:
            return
        
        if self.game_mode == GameMode.RACE:
            # Check if any player has reached the top
            for player_id, board in self.boards.items():
                if board.get_highest_block_position() <= 5:  # Arbitrary threshold for "reaching the top"
                    player = self.players.get(player_id)
                    if player and player.state == PlayerState.PLAYING:
                        player.state = PlayerState.VICTORIOUS
                        self.game_state = GameState.VICTORY
                        return
        
        elif self.game_mode == GameMode.SURVIVAL:
            # Check if only one player is left
            active_players = [
                player_id for player_id, player in self.players.items()
                if player.state == PlayerState.PLAYING
            ]
            
            if len(active_players) == 1:
                self.players[active_players[0]].state = PlayerState.VICTORIOUS
                self.game_state = GameState.VICTORY
            elif len(active_players) == 0:
                self.game_state = GameState.GAME_OVER
        
        elif self.game_mode == GameMode.PUZZLE:
            # Check if any player has completed the puzzle
            # This would depend on specific puzzle objectives
            pass
    
    def _handle_ai_player(self, player_id: str, dt: float) -> None:
        """Handle AI player actions."""
        player = self.players.get(player_id)
        if not player or not player.is_ai or not player.current_block:
            return
        
        # Simple AI: move randomly and occasionally rotate
        if random.random() < 0.1:  # 10% chance to move each update
            # Choose a random direction
            direction = random.choice([Direction.LEFT, Direction.RIGHT])
            self.move_block(player_id, direction)
        
        if random.random() < 0.05:  # 5% chance to rotate each update
            self.rotate_block(player_id, clockwise=random.choice([True, False]))
        
        # Occasionally cast spells if available
        if random.random() < 0.01 and player.spells:  # 1% chance each update
            spell = random.choice(player.spells)
            
            # Choose a target based on the spell type
            if spell.target_type == "self":
                target_id = player_id
            else:
                # Choose a random opponent
                opponents = [
                    p_id for p_id in self.players.keys()
                    if p_id != player_id and self.players[p_id].state == PlayerState.PLAYING
                ]
                
                if opponents:
                    target_id = random.choice(opponents)
                else:
                    target_id = player_id
            
            self.cast_spell(player_id, spell.id, target_id)
    
    def _save_game_state(self) -> None:
        """Save the current game state."""
        try:
            game_state = {
                "game_id": self.game_id,
                "game_mode": self.game_mode.name,
                "game_state": self.game_state.name,
                "current_time": self.current_time,
                "start_time": self.start_time,
                "players": {player_id: player.to_dict() for player_id, player in self.players.items()},
                "boards": {player_id: board.to_dict() for player_id, board in self.boards.items()},
                "active_spells": [spell.to_dict() for spell in self.active_spells]
            }
            
            with open(f"game_state_{self.game_id}.json", "w") as f:
                json.dump(game_state, f, indent=2)
            
            logger.info(f"Game state saved: game_state_{self.game_id}.json")
        except Exception as e:
            logger.error(f"Failed to save game state: {e}")
    
    def load_game_state(self, file_path: str) -> bool:
        """Load a game state from a file."""
        try:
            with open(file_path, "r") as f:
                game_state = json.load(f)
            
            with self.lock:
                self.game_id = game_state["game_id"]
                self.game_mode = GameMode[game_state["game_mode"]]
                self.game_state = GameState[game_state["game_state"]]
                self.current_time = game_state["current_time"]
                self.start_time = game_state["start_time"]
                self.last_update_time = time.time()
                
                # Load players
                self.players = {
                    player_id: Player.from_dict(player_data)
                    for player_id, player_data in game_state["players"].items()
                }
                
                # Load boards
                self.boards = {
                    player_id: GameBoard.from_dict(board_data)
                    for player_id, board_data in game_state["boards"].items()
                }
                
                # Load active spells
                self.active_spells = [
                    ActiveSpell.from_dict(spell_data)
                    for spell_data in game_state["active_spells"]
                ]
                
                logger.info(f"Game state loaded from {file_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to load game state: {e}")
            return False
    
    # Player action methods
    
    def move_block(self, player_id: str, direction: Direction) -> bool:
        """Move a player's current block in the specified direction."""
        with self.lock:
            player = self.players.get(player_id)
            if not player or player.state != PlayerState.PLAYING or not player.current_block:
                return False
            
            board = self.boards.get(player_id)
            if not board:
                return False
            
            block = player.current_block
            
            # Save the old position
            old_position = Position(block.position.x, block.position.y)
            
            # Move the block
            block.move(direction)
            
            # Check if the new position is valid
            if not board.can_place_block(block):
                # Revert to the old position
                block.position = old_position
                return False
            
            return True
    
    def rotate_block(self, player_id: str, clockwise: bool = True) -> bool:
        """Rotate a player's current block."""
        with self.lock:
            player = self.players.get(player_id)
            if not player or player.state != PlayerState.PLAYING or not player.current_block:
                return False
            
            board = self.boards.get(player_id)
            if not board:
                return False
            
            block = player.current_block
            
            # Save the old shape and rotation
            old_shape = block.shape
            old_rotation = block.rotation
            
            # Rotate the block
            if clockwise:
                block.rotate_clockwise()
            else:
                block.rotate_counterclockwise()
            
            # Check if the new position is valid
            if not board.can_place_block(block):
                # Try wall kicks (standard SRS wall kick)
                # These are the standard offsets to try when a rotation fails
                offsets = [
                    (1, 0), (-1, 0), (0, 1), (0, -1),  # Basic NESW
                    (2, 0), (-2, 0), (0, 2), (0, -2),  # Extended NESW
                    (1, 1), (-1, 1), (1, -1), (-1, -1)  # Diagonals
                ]
                
                success = False
                original_position = Position(block.position.x, block.position.y)
                
                for offset_x, offset_y in offsets:
                    block.position.x = original_position.x + offset_x
                    block.position.y = original_position.y + offset_y
                    
                    if board.can_place_block(block):
                        success = True
                        break
                
                if not success:
                    # Revert to the old shape and rotation
                    block.shape = old_shape
                    block.rotation = old_rotation
                    block.position = original_position
                    return False
            
            return True
    
    def drop_block(self, player_id: str, hard_drop: bool = False) -> bool:
        """Drop a player's current block."""
        with self.lock:
            player = self.players.get(player_id)
            if not player or player.state != PlayerState.PLAYING or not player.current_block:
                return False
            
            board = self.boards.get(player_id)
            if not board:
                return False
            
            block = player.current_block
            
            if hard_drop:
                # Hard drop: move the block down as far as possible
                drop_distance = 0
                
                while True:
                    old_position = Position(block.position.x, block.position.y)
                    block.position.y += 1
                    
                    if not board.can_place_block(block):
                        block.position = old_position
                        break
                    
                    drop_distance += 1
                
                # Place the block
                if board.place_block(block):
                    player.blocks_placed += 1
                    
                    # Add points for hard drop
                    player.add_score(drop_distance * GameConstants.POINTS_HARD_DROP)
                    
                    # Add the block to the physics engine
                    self.physics_engine.create_block(block)
                    
                    # Check for completed lines
                    completed_lines = board.check_lines()
                    if completed_lines:
                        lines_cleared = board.clear_lines(completed_lines)
                        
                        # Update player stats
                        player.add_lines(lines_cleared)
                        
                        # Calculate score
                        score = self._calculate_score(lines_cleared, player.combo_count)
                        
                        # Apply score multiplier from spells
                        for spell in player.active_spells:
                            if spell.spell.effect == GameConstants.SPELL_EFFECT_MULTIPLY:
                                score = int(score * spell.spell.strength)
                        
                        player.add_score(score)
                        
                        # Update combo count
                        player.combo_count += 1
                    else:
                        # Reset combo count
                        player.combo_count = 0
                    
                    # Give the player their next block
                    self._give_next_block(player_id)
                    
                    return True
            else:
                # Soft drop: move the block down one cell
                old_position = Position(block.position.x, block.position.y)
                block.position.y += 1
                
                if not board.can_place_block(block):
                    block.position = old_position
                    
                    # Place the block
                    if board.place_block(block):
                        player.blocks_placed += 1
                        
                        # Add the block to the physics engine
                        self.physics_engine.create_block(block)
                        
                        # Check for completed lines
                        completed_lines = board.check_lines()
                        if completed_lines:
                            lines_cleared = board.clear_lines(completed_lines)
                            
                            # Update player stats
                            player.add_lines(lines_cleared)
                            
                            # Calculate score
                            score = self._calculate_score(lines_cleared, player.combo_count)
                            
                            # Apply score multiplier from spells
                            for spell in player.active_spells:
                                if spell.spell.effect == GameConstants.SPELL_EFFECT_MULTIPLY:
                                    score = int(score * spell.spell.strength)
                            
                            player.add_score(score)
                            
                            # Update combo count
                            player.combo_count += 1
                        else:
                            # Reset combo count
                            player.combo_count = 0
                        
                        # Give the player their next block
                        self._give_next_block(player_id)
                        
                        return True
                else:
                    # Add points for soft drop
                    player.add_score(GameConstants.POINTS_SOFT_DROP)
                    return True
            
            return False
    
    def cast_spell(self, caster_id: str, spell_id: str, target_id: str) -> bool:
        """Cast a spell."""
        with self.lock:
            caster = self.players.get(caster_id)
            if not caster or caster.state != PlayerState.PLAYING:
                return False
            
            target = self.players.get(target_id)
            if not target or target.state != PlayerState.PLAYING:
                return False
            
            # Find the spell
            spell = next((s for s in caster.spells if s.id == spell_id), None)
            if not spell:
                return False
            
            # Check if the caster has enough mana
            if caster.mana < spell.mana_cost:
                return False
            
            # Cast the spell
            active_spell = caster.cast_spell(spell_id, target_id, self.current_time)
            if not active_spell:
                return False
            
            # Add to global active spells
            self.active_spells.append(active_spell)
            
            return True
    
    def set_player_ready(self, player_id: str, ready: bool = True) -> bool:
        """Set a player's ready state."""
        with self.lock:
            player = self.players.get(player_id)
            if not player:
                return False
            
            if ready:
                player.state = PlayerState.READY
            else:
                player.state = PlayerState.WAITING
            
            return True
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state."""
        with self.lock:
            return {
                "game_id": self.game_id,
                "game_mode": self.game_mode.name,
                "game_state": self.game_state.name,
                "current_time": self.current_time,
                "start_time": self.start_time,
                "elapsed_time": self.current_time - self.start_time if self.start_time > 0 else 0,
                "players": {player_id: player.to_dict() for player_id, player in self.players.items()},
                "active_spells": [spell.to_dict() for spell in self.active_spells]
            }
    
    def get_player_state(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Get a player's state."""
        with self.lock:
            player = self.players.get(player_id)
            if not player:
                return None
            
            board = self.boards.get(player_id)
            if not board:
                return None
            
            return {
                "player": player.to_dict(),
                "board": board.to_dict()
            }


class GameServer:
    """Server for managing multiple games."""
    
    def __init__(self):
        """Initialize the game server."""
        self.games: Dict[str, GameManager] = {}
        self.lock = threading.RLock()
    
    def create_game(self, game_mode: GameMode = GameMode.SURVIVAL) -> str:
        """Create a new game and return its ID."""
        with self.lock:
            game = GameManager(game_mode)
            game.initialize_game()
            self.games[game.game_id] = game
            return game.game_id
    
    def get_game(self, game_id: str) -> Optional[GameManager]:
        """Get a game by ID."""
        with self.lock:
            return self.games.get(game_id)
    
    def remove_game(self, game_id: str) -> bool:
        """Remove a game."""
        with self.lock:
            if game_id in self.games:
                del self.games[game_id]
                return True
            return False
    
    def get_all_games(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all games."""
        with self.lock:
            return {
                game_id: {
                    "game_id": game.game_id,
                    "game_mode": game.game_mode.name,
                    "game_state": game.game_state.name,
                    "player_count": len(game.players),
                    "start_time": game.start_time
                }
                for game_id, game in self.games.items()
            }
    
    def update_all_games(self) -> None:
        """Update all running games."""
        with self.lock:
            for game in list(self.games.values()):
                if game.game_state == GameState.RUNNING:
                    game.update()
    
    def cleanup_inactive_games(self, max_age: float = 3600.0) -> int:
        """Remove inactive games older than max_age seconds."""
        with self.lock:
            current_time = time.time()
            inactive_games = [
                game_id for game_id, game in self.games.items()
                if game.game_state in (GameState.GAME_OVER, GameState.VICTORY) and
                current_time - game.current_time > max_age
            ]
            
            for game_id in inactive_games:
                del self.games[game_id]
            
            return len(inactive_games)


# Example usage
if __name__ == "__main__":
    # Create a game server
    server = GameServer()
    
    # Create a new game
    game_id = server.create_game(GameMode.SURVIVAL)
    game = server.get_game(game_id)
    
    # Add players
    player1_id = game.add_player("Player 1")
    player2_id = game.add_player("Player 2")
    
    # Set players ready
    game.set_player_ready(player1_id)
    game.set_player_ready(player2_id)
    
    # Start the game
    game.start_game()
    
    # Main game loop
    try:
        while game.game_state == GameState.RUNNING:
            game.update()
            time.sleep(0.016)  # ~60 FPS
    except KeyboardInterrupt:
        print("Game interrupted")
    
    # Print final game state
    print(json.dumps(game.get_game_state(), indent=2))
