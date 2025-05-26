import pytest
import asyncio
from .client import GameClient

@pytest.fixture
def client():
    return GameClient()

@pytest.mark.asyncio
async def test_connect_disconnect(client):
    assert await client.connect()
    await client.disconnect()

@pytest.mark.asyncio
async def test_create_game(client):
    assert await client.connect()
    try:
        settings = {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4,
            "time_limit": 300,
            "score_limit": 1000
        }
        assert await client.create_game(settings)
        assert client.game_id is not None
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_join_game(client):
    assert await client.connect()
    try:
        # Создаем игру
        settings = {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4
        }
        assert await client.create_game(settings)
        game_id = client.game_id

        # Создаем второго клиента
        client2 = GameClient()
        assert await client2.connect()
        try:
            # Присоединяемся к игре
            assert await client2.join_game(game_id)
            assert client2.game_id == game_id
        finally:
            await client2.disconnect()
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_leave_game(client):
    assert await client.connect()
    try:
        # Создаем игру
        settings = {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4
        }
        assert await client.create_game(settings)
        assert client.game_id is not None

        # Покидаем игру
        assert await client.leave_game()
        assert client.game_id is None
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_game_actions(client):
    assert await client.connect()
    try:
        # Создаем игру
        settings = {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4
        }
        assert await client.create_game(settings)

        # Отправляем различные действия
        assert await client.send_game_action("move", direction="left")
        assert await client.send_game_action("rotate", angle=90)
        assert await client.send_game_action("drop")
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_invalid_game_action(client):
    assert await client.connect()
    try:
        # Пытаемся отправить действие без создания игры
        assert not await client.send_game_action("move", direction="left")
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_multiple_clients(client):
    assert await client.connect()
    try:
        # Создаем игру
        settings = {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4
        }
        assert await client.create_game(settings)
        game_id = client.game_id

        # Создаем несколько клиентов и присоединяем их к игре
        clients = []
        for _ in range(3):
            new_client = GameClient()
            assert await new_client.connect()
            assert await new_client.join_game(game_id)
            clients.append(new_client)

        # Отправляем действия от всех клиентов
        for c in clients:
            assert await c.send_game_action("move", direction="left")

        # Отключаем всех клиентов
        for c in clients:
            await c.disconnect()
    finally:
        await client.disconnect() 