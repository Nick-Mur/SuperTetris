import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

class GameLogger:
    """Класс для настройки и использования логирования в игре"""
    
    def __init__(
        self,
        name: str = "game_server",
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Создаем директорию для логов если её нет
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Настраиваем логгер
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка логгера"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Форматтер для логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Хендлер для файла
        log_file = os.path.join(
            self.log_dir,
            f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setFormatter(formatter)
        
        # Хендлер для консоли
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Добавляем хендлеры к логгеру
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def debug(self, message: str, *args, **kwargs):
        """Логирование отладочной информации"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Логирование информационных сообщений"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Логирование предупреждений"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Логирование ошибок"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Логирование критических ошибок"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """Логирование исключений"""
        self.logger.exception(message, *args, **kwargs)

# Примеры использования
def game_events_example():
    """Пример логирования игровых событий"""
    logger = GameLogger(log_level="DEBUG")
    
    # Логирование создания игры
    logger.info("Создана новая игра", extra={
        "game_id": "123",
        "game_type": "classic",
        "max_players": 4
    })
    
    # Логирование подключения игрока
    logger.info("Игрок подключился", extra={
        "player_id": "456",
        "game_id": "123"
    })
    
    # Логирование игрового действия
    logger.debug("Игровое действие", extra={
        "player_id": "456",
        "game_id": "123",
        "action": "move",
        "direction": "left"
    })
    
    # Логирование ошибки
    try:
        raise ValueError("Неверное игровое действие")
    except Exception as e:
        logger.error("Ошибка при обработке действия", extra={
            "player_id": "456",
            "game_id": "123",
            "error": str(e)
        })

def session_events_example():
    """Пример логирования событий сессии"""
    logger = GameLogger(log_level="INFO")
    
    # Логирование создания сессии
    logger.info("Создана новая сессия", extra={
        "session_id": "789",
        "user_id": "456"
    })
    
    # Логирование активности сессии
    logger.debug("Обновлена активность сессии", extra={
        "session_id": "789",
        "last_activity": datetime.now().isoformat()
    })
    
    # Логирование истечения сессии
    logger.warning("Сессия истекла", extra={
        "session_id": "789",
        "user_id": "456",
        "duration": "3600"
    })

def network_events_example():
    """Пример логирования сетевых событий"""
    logger = GameLogger(log_level="DEBUG")
    
    # Логирование подключения
    logger.info("Новое WebSocket подключение", extra={
        "client_id": "abc",
        "ip": "127.0.0.1"
    })
    
    # Логирование сообщения
    logger.debug("Получено сообщение", extra={
        "client_id": "abc",
        "message_type": "game_action",
        "message_size": 1024
    })
    
    # Логирование отключения
    logger.info("Клиент отключился", extra={
        "client_id": "abc",
        "duration": "300"
    })
    
    # Логирование ошибки сети
    logger.error("Ошибка сети", extra={
        "client_id": "abc",
        "error": "Connection reset"
    })

if __name__ == "__main__":
    # Запускаем примеры
    print("Примеры логирования игровых событий:")
    game_events_example()
    
    print("\nПримеры логирования событий сессии:")
    session_events_example()
    
    print("\nПримеры логирования сетевых событий:")
    network_events_example() 