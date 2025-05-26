from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Основные настройки сервера
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8080"))
    
    # Настройки игры
    game_update_interval: float = float(os.getenv("GAME_UPDATE_INTERVAL", "0.016"))  # ~60 FPS
    
    # Настройки сессии
    session_cleanup_interval: int = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))  # 5 минут
    session_heartbeat_interval: int = int(os.getenv("SESSION_HEARTBEAT_INTERVAL", "30"))  # 30 секунд
    
    # Настройки физики
    physics_gravity: float = float(os.getenv("PHYSICS_GRAVITY", "9.8"))
    physics_friction: float = float(os.getenv("PHYSICS_FRICTION", "0.1"))
    
    # Настройки логирования
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", "logs/server.log")
    
    class Config:
        env_file = ".env" 