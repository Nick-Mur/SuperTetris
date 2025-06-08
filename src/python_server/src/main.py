import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from .logger import logger
import uuid
from typing import Dict, Set
import uvicorn.logging
from .config import Settings
from .game.manager import GameManager
from .session.manager import SessionManager
from .network.manager import NetworkManager
from .physics.manager import PhysicsManager
from .exceptions import GameError, SessionNotFoundError, NetworkError

app = FastAPI(title="Tetris Game Server")
settings = Settings()

# Инициализация менеджеров
game_manager = GameManager()
session_manager = SessionManager(game_manager)
network_manager = NetworkManager(settings)
physics_manager = PhysicsManager()

# Хранение активных WebSocket соединений
active_connections: Dict[uuid.UUID, WebSocket] = {}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting server...")
    await physics_manager.start()
    await game_manager.start()
    await session_manager.start()
    await network_manager.start()
    logger.info("Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping server...")
    await network_manager.stop()
    await session_manager.stop()
    await game_manager.stop()
    await physics_manager.stop()
    logger.info("Server stopped successfully")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    connection_id = uuid.uuid4()
    await websocket.accept()
    active_connections[connection_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            await network_manager.handle_message(connection_id, data)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    ) 