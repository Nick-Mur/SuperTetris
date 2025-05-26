import asyncio
import json
import uuid
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameClient:
    def __init__(self, server_url: str = "ws://localhost:8080/ws"):
        self.server_url = server_url
        self.websocket = None
        self.session_id = None
        self.game_id = None

    async def connect(self):
        """Устанавливает WebSocket соединение с сервером"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            logger.info("Connected to server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False

    async def disconnect(self):
        """Закрывает WebSocket соединение"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from server")

    async def create_game(self, settings: dict):
        """Создает новую игру"""
        message = {
            "type": "create_game",
            "settings": settings
        }
        await self._send_message(message)
        response = await self._receive_message()
        if response["type"] == "success":
            self.game_id = response["data"]["game_id"]
            logger.info(f"Game created: {self.game_id}")
            return True
        return False

    async def join_game(self, game_id: str):
        """Присоединяется к существующей игре"""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())

        message = {
            "type": "join_game",
            "game_id": game_id,
            "session_id": self.session_id
        }
        await self._send_message(message)
        response = await self._receive_message()
        if response["type"] == "success":
            self.game_id = game_id
            logger.info(f"Joined game: {game_id}")
            return True
        return False

    async def leave_game(self):
        """Покидает текущую игру"""
        if not self.session_id:
            return False

        message = {
            "type": "leave_game",
            "session_id": self.session_id
        }
        await self._send_message(message)
        response = await self._receive_message()
        if response["type"] == "success":
            self.game_id = None
            logger.info("Left game")
            return True
        return False

    async def send_game_action(self, action: str, **kwargs):
        """Отправляет игровое действие"""
        if not self.game_id:
            return False

        message = {
            "type": "game_action",
            "game_id": self.game_id,
            "action": action,
            **kwargs
        }
        await self._send_message(message)
        response = await self._receive_message()
        return response["type"] == "success"

    async def _send_message(self, message: dict):
        """Отправляет сообщение на сервер"""
        if not self.websocket:
            raise ConnectionError("Not connected to server")
        await self.websocket.send(json.dumps(message))

    async def _receive_message(self) -> dict:
        """Получает сообщение от сервера"""
        if not self.websocket:
            raise ConnectionError("Not connected to server")
        response = await self.websocket.recv()
        return json.loads(response)

async def main():
    # Пример использования клиента
    client = GameClient()
    
    try:
        # Подключаемся к серверу
        if not await client.connect():
            return

        # Создаем новую игру
        settings = {
            "game_type": "classic",
            "difficulty": "medium",
            "max_players": 4,
            "time_limit": 300,
            "score_limit": 1000
        }
        if not await client.create_game(settings):
            return

        # Отправляем несколько игровых действий
        await client.send_game_action("move", direction="left")
        await client.send_game_action("rotate", angle=90)
        await client.send_game_action("drop")

        # Ждем немного
        await asyncio.sleep(5)

        # Покидаем игру
        await client.leave_game()

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 