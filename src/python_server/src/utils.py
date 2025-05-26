import json
import uuid
from typing import Any, Dict, Optional
from loguru import logger
from .exceptions import GameError

def validate_game_settings(settings: Dict[str, Any]) -> None:
    """Проверяет корректность настроек игры"""
    required_fields = ["game_type", "difficulty", "max_players"]
    for field in required_fields:
        if field not in settings:
            raise GameError(f"Missing required field: {field}")

    if not isinstance(settings["max_players"], int) or settings["max_players"] < 1:
        raise GameError("max_players must be a positive integer")

    if "time_limit" in settings and settings["time_limit"] is not None:
        if not isinstance(settings["time_limit"], int) or settings["time_limit"] < 0:
            raise GameError("time_limit must be a non-negative integer")

    if "score_limit" in settings and settings["score_limit"] is not None:
        if not isinstance(settings["score_limit"], int) or settings["score_limit"] < 0:
            raise GameError("score_limit must be a non-negative integer")

def parse_uuid(uuid_str: str) -> Optional[uuid.UUID]:
    """Преобразует строку в UUID"""
    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        return None

def format_error(error: Exception) -> Dict[str, Any]:
    """Форматирует ошибку для отправки клиенту"""
    return {
        "type": "error",
        "error": error.__class__.__name__,
        "message": str(error)
    }

def format_success(data: Dict[str, Any]) -> Dict[str, Any]:
    """Форматирует успешный ответ для отправки клиенту"""
    return {
        "type": "success",
        "data": data
    }

def safe_json_loads(data: str) -> Optional[Dict[str, Any]]:
    """Безопасно парсит JSON"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        return None

def safe_json_dumps(data: Dict[str, Any]) -> Optional[str]:
    """Безопасно сериализует в JSON"""
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize to JSON: {e}")
        return None 