"""Server configuration using `pydantic_settings`."""

from typing import Optional

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    """Configuration for the game server."""

    # Основные настройки сервера
    server_host: str = "0.0.0.0"
    server_port: int = 8080

    # Настройки игры
    game_update_interval: float = 0.016

    # Настройки сессии
    session_cleanup_interval: int = 300
    session_heartbeat_interval: int = 30

    # Настройки физики
    physics_gravity: float = 9.8
    physics_friction: float = 0.1

    # Настройки логирования
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/server.log"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

