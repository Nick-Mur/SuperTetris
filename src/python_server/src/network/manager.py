import json
import uuid
from typing import Dict, Any, Optional
from loguru import logger
from ..config import Settings
from ..game.manager import GameManager
from ..session.manager import SessionManager

class NetworkManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.game_manager: Optional[GameManager] = None
        self.session_manager: Optional[SessionManager] = None
        self.active_connections: Dict[uuid.UUID, Any] = {}

    def set_managers(self, game_manager: GameManager, session_manager: SessionManager) -> None:
        self.game_manager = game_manager
        self.session_manager = session_manager

    async def handle_message(self, connection_id: uuid.UUID, message: str) -> None:
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if not message_type:
                logger.error(f"Message type not found in message: {message}")
                return

            handler = getattr(self, f"_handle_{message_type}", None)
            if handler:
                await handler(connection_id, data)
            else:
                logger.error(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _handle_create_game(self, connection_id: uuid.UUID, data: Dict[str, Any]) -> None:
        if not self.game_manager:
            return
        game_id = await self.game_manager.create_game()
        await self._send_response(connection_id, {
            "type": "game_created",
            "game_id": str(game_id)
        })

    async def _handle_join_game(self, connection_id: uuid.UUID, data: Dict[str, Any]) -> None:
        if not self.session_manager or not self.game_manager:
            return
        
        game_id = uuid.UUID(data.get("game_id"))
        session_id = uuid.UUID(data.get("session_id"))
        
        await self.session_manager.join_game(session_id, game_id)
        await self._send_response(connection_id, {
            "type": "game_joined",
            "game_id": str(game_id)
        })

    async def _handle_leave_game(self, connection_id: uuid.UUID, data: Dict[str, Any]) -> None:
        if not self.session_manager:
            return
        
        session_id = uuid.UUID(data.get("session_id"))
        await self.session_manager.leave_game(session_id)
        await self._send_response(connection_id, {
            "type": "game_left"
        })

    async def _handle_game_action(self, connection_id: uuid.UUID, data: Dict[str, Any]) -> None:
        if not self.game_manager:
            return
        
        game_id = uuid.UUID(data.get("game_id"))
        action = data.get("action")
        
        if game := await self.game_manager.get_game(game_id):
            # Здесь будет обработка игровых действий
            await self._send_response(connection_id, {
                "type": "action_processed",
                "action": action
            })

    async def _send_response(self, connection_id: uuid.UUID, data: Dict[str, Any]) -> None:
        if connection := self.active_connections.get(connection_id):
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Error sending response: {e}")

    async def start(self) -> None:
        logger.info("Network manager started")

    async def stop(self) -> None:
        self.active_connections.clear()
        logger.info("Network manager stopped") 