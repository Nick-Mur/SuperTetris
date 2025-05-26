import asyncio
import uuid
from typing import Dict, Optional
from loguru import logger
from ..config import Settings

class Game:
    def __init__(self, game_id: uuid.UUID, settings: Settings):
        self.id = game_id
        self.players: set[uuid.UUID] = set()
        self.running = False
        self.settings = settings
        self.update_task: Optional[asyncio.Task] = None

    async def add_player(self, player_id: uuid.UUID) -> None:
        self.players.add(player_id)

    async def remove_player(self, player_id: uuid.UUID) -> None:
        self.players.discard(player_id)

    async def is_empty(self) -> bool:
        return len(self.players) == 0

    async def is_running(self) -> bool:
        return self.running

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.update_task = asyncio.create_task(self._update_loop())

    async def stop(self) -> None:
        if not self.running:
            return
        self.running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

    async def _update_loop(self) -> None:
        while self.running:
            try:
                # Здесь будет логика обновления игры
                await asyncio.sleep(self.settings.game_update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in game update loop: {e}")

class GameManager:
    def __init__(self):
        self.games: Dict[uuid.UUID, Game] = {}
        self.settings = Settings()

    async def create_game(self) -> uuid.UUID:
        game_id = uuid.uuid4()
        self.games[game_id] = Game(game_id, self.settings)
        return game_id

    async def get_game(self, game_id: uuid.UUID) -> Optional[Game]:
        return self.games.get(game_id)

    async def remove_game(self, game_id: uuid.UUID) -> None:
        if game := self.games.get(game_id):
            await game.stop()
            del self.games[game_id]

    async def add_player_to_game(self, player_id: uuid.UUID, game_id: uuid.UUID) -> None:
        if game := self.games.get(game_id):
            await game.add_player(player_id)

    async def remove_player_from_game(self, player_id: uuid.UUID, game_id: uuid.UUID) -> None:
        if game := self.games.get(game_id):
            await game.remove_player(player_id)
            if await game.is_empty():
                await self.remove_game(game_id)

    async def start(self) -> None:
        logger.info("Game manager started")

    async def stop(self) -> None:
        for game in self.games.values():
            await game.stop()
        self.games.clear()
        logger.info("Game manager stopped") 