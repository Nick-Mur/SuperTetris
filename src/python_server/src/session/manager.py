import asyncio
import uuid
from typing import Dict, Optional
from ..logger import logger
from ..config import Settings
from ..game.manager import GameManager

class Session:
    def __init__(self, session_id: uuid.UUID, user_id: uuid.UUID):
        self.id = session_id
        self.user_id = user_id
        self.game_id: Optional[uuid.UUID] = None
        self.last_activity = asyncio.get_event_loop().time()

    def update_activity(self) -> None:
        self.last_activity = asyncio.get_event_loop().time()

    def is_expired(self, timeout: float) -> bool:
        return (asyncio.get_event_loop().time() - self.last_activity) > timeout

class SessionManager:
    def __init__(self, game_manager: GameManager):
        self.sessions: Dict[uuid.UUID, Session] = {}
        self.game_manager = game_manager
        self.settings = Settings()
        self.cleanup_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None

    async def create_session(self, user_id: uuid.UUID) -> uuid.UUID:
        session_id = uuid.uuid4()
        self.sessions[session_id] = Session(session_id, user_id)
        return session_id

    async def get_session(self, session_id: uuid.UUID) -> Optional[Session]:
        return self.sessions.get(session_id)

    async def remove_session(self, session_id: uuid.UUID) -> None:
        if session := self.sessions.get(session_id):
            if session.game_id:
                await self.game_manager.remove_player_from_game(
                    session.user_id, session.game_id
                )
            del self.sessions[session_id]

    async def join_game(self, session_id: uuid.UUID, game_id: uuid.UUID) -> None:
        if session := self.sessions.get(session_id):
            if session.game_id:
                await self.game_manager.remove_player_from_game(
                    session.user_id, session.game_id
                )
            session.game_id = game_id
            await self.game_manager.add_player_to_game(session.user_id, game_id)
            session.update_activity()

    async def leave_game(self, session_id: uuid.UUID) -> None:
        if session := self.sessions.get(session_id):
            if session.game_id:
                await self.game_manager.remove_player_from_game(
                    session.user_id, session.game_id
                )
                session.game_id = None
            session.update_activity()

    async def _cleanup_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.settings.session_cleanup_interval)
                await self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _heartbeat_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self.settings.session_heartbeat_interval)
                await self._send_heartbeats()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")

    async def _cleanup_expired_sessions(self) -> None:
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.is_expired(self.settings.session_cleanup_interval)
        ]
        for session_id in expired_sessions:
            await self.remove_session(session_id)

    async def _send_heartbeats(self) -> None:
        for session in self.sessions.values():
            if session.game_id:
                # Здесь будет логика отправки heartbeat
                session.update_activity()

    async def start(self) -> None:
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("Session manager started")

    async def stop(self) -> None:
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass

        for session_id in list(self.sessions.keys()):
            await self.remove_session(session_id)
        logger.info("Session manager stopped") 