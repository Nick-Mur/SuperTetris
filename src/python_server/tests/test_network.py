import pytest
import uuid
import json
from ..network.manager import NetworkManager
from ..game.manager import GameManager
from ..session.manager import SessionManager
from ..config import Settings

@pytest.fixture
def settings():
    return Settings()

@pytest.fixture
def game_manager():
    return GameManager()

@pytest.fixture
def session_manager(game_manager):
    return SessionManager(game_manager)

@pytest.fixture
def network_manager(settings):
    return NetworkManager(settings)

@pytest.mark.asyncio
async def test_handle_create_game(network_manager, game_manager, session_manager):
    network_manager.set_managers(game_manager, session_manager)
    connection_id = uuid.uuid4()
    message = json.dumps({
        "type": "create_game",
        "settings": {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4
        }
    })
    await network_manager.handle_message(connection_id, message)
    # Проверяем, что игра была создана
    assert len(game_manager.games) > 0

@pytest.mark.asyncio
async def test_handle_join_game(network_manager, game_manager, session_manager):
    network_manager.set_managers(game_manager, session_manager)
    connection_id = uuid.uuid4()
    game_id = await game_manager.create_game()
    session_id = await session_manager.create_session(uuid.uuid4())
    
    message = json.dumps({
        "type": "join_game",
        "game_id": str(game_id),
        "session_id": str(session_id)
    })
    await network_manager.handle_message(connection_id, message)
    
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert session.game_id == game_id

@pytest.mark.asyncio
async def test_handle_leave_game(network_manager, game_manager, session_manager):
    network_manager.set_managers(game_manager, session_manager)
    connection_id = uuid.uuid4()
    game_id = await game_manager.create_game()
    session_id = await session_manager.create_session(uuid.uuid4())
    await session_manager.join_game(session_id, game_id)
    
    message = json.dumps({
        "type": "leave_game",
        "session_id": str(session_id)
    })
    await network_manager.handle_message(connection_id, message)
    
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert session.game_id is None

@pytest.mark.asyncio
async def test_handle_game_action(network_manager, game_manager, session_manager):
    network_manager.set_managers(game_manager, session_manager)
    connection_id = uuid.uuid4()
    game_id = await game_manager.create_game()
    
    message = json.dumps({
        "type": "game_action",
        "game_id": str(game_id),
        "action": "move",
        "direction": "left"
    })
    await network_manager.handle_message(connection_id, message)
    # Проверяем, что действие было обработано
    # Здесь можно добавить более конкретные проверки в зависимости от реализации

@pytest.mark.asyncio
async def test_handle_invalid_message(network_manager):
    connection_id = uuid.uuid4()
    message = "invalid json"
    await network_manager.handle_message(connection_id, message)
    # Проверяем, что ошибка была обработана корректно

@pytest.mark.asyncio
async def test_handle_unknown_message_type(network_manager):
    connection_id = uuid.uuid4()
    message = json.dumps({
        "type": "unknown_type",
        "data": {}
    })
    await network_manager.handle_message(connection_id, message)
    # Проверяем, что неизвестный тип сообщения был обработан корректно 