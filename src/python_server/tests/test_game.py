import pytest
import uuid
from ..src.game.manager import GameManager, Game
from ..src.game.types import GameType, DifficultyLevel, GameSettings
from ..src.exceptions import GameNotFoundError, GameAlreadyExistsError

@pytest.fixture
def game_manager():
    return GameManager()

@pytest.fixture
def game_settings():
    return {
        "game_type": GameType.CLASSIC,
        "difficulty": DifficultyLevel.MEDIUM,
        "max_players": 4,
        "time_limit": 300,
        "score_limit": 1000
    }

@pytest.mark.asyncio
async def test_create_game(game_manager, game_settings):
    game_id = await game_manager.create_game()
    assert game_id is not None
    assert isinstance(game_id, uuid.UUID)

@pytest.mark.asyncio
async def test_get_game(game_manager, game_settings):
    game_id = await game_manager.create_game()
    game = await game_manager.get_game(game_id)
    assert game is not None
    assert isinstance(game, Game)

@pytest.mark.asyncio
async def test_get_nonexistent_game(game_manager):
    game_id = uuid.uuid4()
    game = await game_manager.get_game(game_id)
    assert game is None

@pytest.mark.asyncio
async def test_remove_game(game_manager, game_settings):
    game_id = await game_manager.create_game()
    await game_manager.remove_game(game_id)
    game = await game_manager.get_game(game_id)
    assert game is None

@pytest.mark.asyncio
async def test_add_player_to_game(game_manager, game_settings):
    game_id = await game_manager.create_game()
    player_id = uuid.uuid4()
    await game_manager.add_player_to_game(player_id, game_id)
    game = await game_manager.get_game(game_id)
    assert game is not None
    assert player_id in game.players

@pytest.mark.asyncio
async def test_remove_player_from_game(game_manager, game_settings):
    game_id = await game_manager.create_game()
    player1 = uuid.uuid4()
    player2 = uuid.uuid4()
    await game_manager.add_player_to_game(player1, game_id)
    await game_manager.add_player_to_game(player2, game_id)
    await game_manager.remove_player_from_game(player1, game_id)
    game = await game_manager.get_game(game_id)
    assert game is not None
    assert player1 not in game.players
    assert player2 in game.players

@pytest.mark.asyncio
async def test_game_is_empty_after_removing_last_player(game_manager, game_settings):
    game_id = await game_manager.create_game()
    player_id = uuid.uuid4()
    await game_manager.add_player_to_game(player_id, game_id)
    await game_manager.remove_player_from_game(player_id, game_id)
    game = await game_manager.get_game(game_id)
    assert game is None 