from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Configuration for the game server."""

    # Основные настройки сервера
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8080"))

    # Настройки игры
    game_update_interval: float = float(os.getenv("GAME_UPDATE_INTERVAL", "0.016"))

    # Настройки сессии
    session_cleanup_interval: int = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))
    session_heartbeat_interval: int = int(os.getenv("SESSION_HEARTBEAT_INTERVAL", "30"))

    # Настройки физики
    physics_gravity: float = float(os.getenv("PHYSICS_GRAVITY", "9.8"))
    physics_friction: float = float(os.getenv("PHYSICS_FRICTION", "0.1"))

    # Настройки логирования
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", "logs/server.log")

    model_config = ConfigDict(env_file=".env")

