import asyncio
import uuid
from typing import Dict, Optional, Tuple
from ..logger import logger
from ..config import Settings

class PhysicsManager:
    def __init__(self):
        self.settings = Settings()
        self.blocks: Dict[uuid.UUID, Dict] = {}
        self.running = False
        self.update_task: Optional[asyncio.Task] = None

    async def add_block(self, block_id: uuid.UUID, position: Tuple[float, float], rotation: float) -> None:
        self.blocks[block_id] = {
            "position": position,
            "rotation": rotation,
            "velocity": (0.0, 0.0),
            "angular_velocity": 0.0
        }

    async def remove_block(self, block_id: uuid.UUID) -> None:
        self.blocks.pop(block_id, None)

    async def update_block_position(self, block_id: uuid.UUID, position: Tuple[float, float]) -> None:
        if block := self.blocks.get(block_id):
            block["position"] = position

    async def update_block_rotation(self, block_id: uuid.UUID, rotation: float) -> None:
        if block := self.blocks.get(block_id):
            block["rotation"] = rotation

    async def apply_force(self, block_id: uuid.UUID, force: Tuple[float, float]) -> None:
        if block := self.blocks.get(block_id):
            vx, vy = block["velocity"]
            fx, fy = force
            block["velocity"] = (vx + fx, vy + fy)

    async def apply_torque(self, block_id: uuid.UUID, torque: float) -> None:
        if block := self.blocks.get(block_id):
            block["angular_velocity"] += torque

    async def _update_loop(self) -> None:
        while self.running:
            try:
                await self._update_physics()
                await asyncio.sleep(self.settings.game_update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in physics update loop: {e}")

    async def _update_physics(self) -> None:
        for block_id, block in self.blocks.items():
            # Применяем гравитацию
            vx, vy = block["velocity"]
            vy += self.settings.physics_gravity * self.settings.game_update_interval

            # Применяем трение
            vx *= (1.0 - self.settings.physics_friction)
            vy *= (1.0 - self.settings.physics_friction)

            # Обновляем позицию
            x, y = block["position"]
            x += vx * self.settings.game_update_interval
            y += vy * self.settings.game_update_interval

            # Обновляем состояние блока
            block["position"] = (x, y)
            block["velocity"] = (vx, vy)
            block["angular_velocity"] *= (1.0 - self.settings.physics_friction)

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.update_task = asyncio.create_task(self._update_loop())
        logger.info("Physics manager started")

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
        self.blocks.clear()
        logger.info("Physics manager stopped") 