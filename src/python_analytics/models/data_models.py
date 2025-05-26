from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

@dataclass
class GameEvent:
    """Событие в игре"""
    event_id: UUID
    game_id: UUID
    player_id: UUID
    event_type: str
    timestamp: datetime
    data: Dict[str, Union[str, int, float, bool]]
    
@dataclass
class PlayerAction:
    """Действие игрока"""
    action_id: UUID
    player_id: UUID
    game_id: UUID
    action_type: str
    timestamp: datetime
    success: bool
    data: Dict[str, Union[str, int, float, bool]]
    
@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    metrics_id: UUID
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    network_latency: float
    game_fps: float
    active_players: int
    active_games: int
    
@dataclass
class GameplayMetrics:
    """Метрики геймплея"""
    game_id: UUID
    player_id: UUID
    score: int
    lines_cleared: int
    time_played: int
    pieces_placed: int
    level: int
    timestamp: datetime
    
@dataclass
class PlayerMetrics:
    """Метрики игрока"""
    player_id: UUID
    total_games: int
    total_score: int
    total_time_played: int
    average_score: float
    win_rate: float
    last_active: datetime
    
@dataclass
class AnalyticsResults:
    """Результаты анализа"""
    gameplay_results: Dict[str, Union[float, int, List[float]]]
    player_results: Dict[str, Union[float, int, List[float]]]
    balance_results: Dict[str, Union[float, int, List[float]]]
    performance_results: Dict[str, Union[float, int, List[float]]]
    timestamp: datetime 