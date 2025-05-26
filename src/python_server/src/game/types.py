from enum import Enum
from typing import TypedDict, Optional
from uuid import UUID

class GameType(str, Enum):
    CLASSIC = "classic"
    BATTLE = "battle"
    COOPERATIVE = "cooperative"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class GameSettings(TypedDict):
    game_type: GameType
    difficulty: DifficultyLevel
    max_players: int
    time_limit: Optional[int]  # в секундах
    score_limit: Optional[int]

class GameState(TypedDict):
    game_id: UUID
    players: list[UUID]
    settings: GameSettings
    is_running: bool
    current_score: int
    time_remaining: Optional[int]  # в секундах

class PlayerState(TypedDict):
    player_id: UUID
    score: int
    level: int
    lines_cleared: int
    is_active: bool 