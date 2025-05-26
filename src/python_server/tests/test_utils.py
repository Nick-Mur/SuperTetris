import pytest
import uuid
from ..utils import (
    validate_game_settings,
    parse_uuid,
    format_error,
    format_success,
    safe_json_loads,
    safe_json_dumps
)
from ..exceptions import GameError

def test_validate_game_settings_valid():
    settings = {
        "game_type": "classic",
        "difficulty": "medium",
        "max_players": 4,
        "time_limit": 300,
        "score_limit": 1000
    }
    validate_game_settings(settings)  # Не должно вызывать исключение

def test_validate_game_settings_missing_required():
    settings = {
        "game_type": "classic",
        "difficulty": "medium"
        # Отсутствует max_players
    }
    with pytest.raises(GameError):
        validate_game_settings(settings)

def test_validate_game_settings_invalid_max_players():
    settings = {
        "game_type": "classic",
        "difficulty": "medium",
        "max_players": 0  # Должно быть положительным
    }
    with pytest.raises(GameError):
        validate_game_settings(settings)

def test_validate_game_settings_invalid_time_limit():
    settings = {
        "game_type": "classic",
        "difficulty": "medium",
        "max_players": 4,
        "time_limit": -1  # Должно быть неотрицательным
    }
    with pytest.raises(GameError):
        validate_game_settings(settings)

def test_parse_uuid_valid():
    uuid_str = str(uuid.uuid4())
    parsed = parse_uuid(uuid_str)
    assert parsed is not None
    assert isinstance(parsed, uuid.UUID)
    assert str(parsed) == uuid_str

def test_parse_uuid_invalid():
    invalid_uuid = "not-a-uuid"
    parsed = parse_uuid(invalid_uuid)
    assert parsed is None

def test_format_error():
    error = GameError("Test error")
    formatted = format_error(error)
    assert formatted["type"] == "error"
    assert formatted["error"] == "GameError"
    assert formatted["message"] == "Test error"

def test_format_success():
    data = {"key": "value"}
    formatted = format_success(data)
    assert formatted["type"] == "success"
    assert formatted["data"] == data

def test_safe_json_loads_valid():
    json_str = '{"key": "value"}'
    result = safe_json_loads(json_str)
    assert result is not None
    assert result["key"] == "value"

def test_safe_json_loads_invalid():
    json_str = "invalid json"
    result = safe_json_loads(json_str)
    assert result is None

def test_safe_json_dumps_valid():
    data = {"key": "value"}
    result = safe_json_dumps(data)
    assert result is not None
    assert result == '{"key": "value"}'

def test_safe_json_dumps_invalid():
    class Unserializable:
        pass
    
    data = {"key": Unserializable()}
    result = safe_json_dumps(data)
    assert result is None 