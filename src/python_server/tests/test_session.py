import pytest
import uuid
import asyncio
from ..session.manager import SessionManager, Session
from ..game.manager import GameManager
from ..exceptions import SessionNotFoundError

@pytest.fixture
def game_manager():
    return GameManager()

@pytest.fixture
def session_manager(game_manager):
    return SessionManager(game_manager)

@pytest.mark.asyncio
async def test_create_session(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    assert session_id is not None
    assert isinstance(session_id, uuid.UUID)

@pytest.mark.asyncio
async def test_get_session(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert isinstance(session, Session)
    assert session.user_id == user_id

@pytest.mark.asyncio
async def test_get_nonexistent_session(session_manager):
    session_id = uuid.uuid4()
    session = await session_manager.get_session(session_id)
    assert session is None

@pytest.mark.asyncio
async def test_remove_session(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    await session_manager.remove_session(session_id)
    session = await session_manager.get_session(session_id)
    assert session is None

@pytest.mark.asyncio
async def test_join_game(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    game_id = await session_manager.game_manager.create_game()
    await session_manager.join_game(session_id, game_id)
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert session.game_id == game_id

@pytest.mark.asyncio
async def test_leave_game(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    game_id = await session_manager.game_manager.create_game()
    await session_manager.join_game(session_id, game_id)
    await session_manager.leave_game(session_id)
    session = await session_manager.get_session(session_id)
    assert session is not None
    assert session.game_id is None

@pytest.mark.asyncio
async def test_session_activity_update(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    session = await session_manager.get_session(session_id)
    initial_activity = session.last_activity
    await asyncio.sleep(0.1)
    session.update_activity()
    assert session.last_activity > initial_activity

@pytest.mark.asyncio
async def test_session_expiration(session_manager):
    user_id = uuid.uuid4()
    session_id = await session_manager.create_session(user_id)
    session = await session_manager.get_session(session_id)
    assert not session.is_expired(1.0)  # Не истекла
    await asyncio.sleep(1.1)
    assert session.is_expired(1.0)  # Истекла 