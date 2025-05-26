from typing import Dict, Any
import os

# Пример базовой конфигурации
BASE_CONFIG: Dict[str, Any] = {
    "host": "localhost",
    "port": 8000,
    "game_update_interval": 0.016,  # 60 FPS
    "physics_update_interval": 0.016,
    "session_cleanup_interval": 300,  # 5 минут
    "session_timeout": 3600,  # 1 час
    "max_players_per_game": 4,
    "log_level": "INFO"
}

# Пример конфигурации для разработки
DEV_CONFIG: Dict[str, Any] = {
    **BASE_CONFIG,
    "host": "0.0.0.0",  # Разрешаем подключения с любого IP
    "log_level": "DEBUG",
    "debug": True,
    "game_update_interval": 0.033,  # 30 FPS для разработки
    "physics_update_interval": 0.033
}

# Пример конфигурации для продакшена
PROD_CONFIG: Dict[str, Any] = {
    **BASE_CONFIG,
    "host": "0.0.0.0",
    "port": 80,  # Стандартный HTTP порт
    "log_level": "WARNING",
    "debug": False,
    "session_timeout": 1800,  # 30 минут
    "max_players_per_game": 8
}

# Пример конфигурации для тестирования
TEST_CONFIG: Dict[str, Any] = {
    **BASE_CONFIG,
    "host": "localhost",
    "port": 8001,  # Другой порт для тестов
    "log_level": "DEBUG",
    "debug": True,
    "game_update_interval": 0.1,  # Медленнее для тестов
    "physics_update_interval": 0.1,
    "session_timeout": 60  # 1 минута для тестов
}

# Функция для загрузки конфигурации из переменных окружения
def load_config_from_env() -> Dict[str, Any]:
    config = BASE_CONFIG.copy()
    
    # Загружаем значения из переменных окружения
    if "HOST" in os.environ:
        config["host"] = os.environ["HOST"]
    if "PORT" in os.environ:
        config["port"] = int(os.environ["PORT"])
    if "GAME_UPDATE_INTERVAL" in os.environ:
        config["game_update_interval"] = float(os.environ["GAME_UPDATE_INTERVAL"])
    if "PHYSICS_UPDATE_INTERVAL" in os.environ:
        config["physics_update_interval"] = float(os.environ["PHYSICS_UPDATE_INTERVAL"])
    if "SESSION_CLEANUP_INTERVAL" in os.environ:
        config["session_cleanup_interval"] = int(os.environ["SESSION_CLEANUP_INTERVAL"])
    if "SESSION_TIMEOUT" in os.environ:
        config["session_timeout"] = int(os.environ["SESSION_TIMEOUT"])
    if "MAX_PLAYERS_PER_GAME" in os.environ:
        config["max_players_per_game"] = int(os.environ["MAX_PLAYERS_PER_GAME"])
    if "LOG_LEVEL" in os.environ:
        config["log_level"] = os.environ["LOG_LEVEL"]
    if "DEBUG" in os.environ:
        config["debug"] = os.environ["DEBUG"].lower() == "true"
    
    return config

# Пример использования конфигурации
def get_config(env: str = "development") -> Dict[str, Any]:
    """
    Получение конфигурации в зависимости от окружения
    
    Args:
        env: Окружение (development, production, testing)
    
    Returns:
        Dict[str, Any]: Конфигурация для указанного окружения
    """
    configs = {
        "development": DEV_CONFIG,
        "production": PROD_CONFIG,
        "testing": TEST_CONFIG
    }
    
    # Получаем базовую конфигурацию для окружения
    config = configs.get(env, BASE_CONFIG).copy()
    
    # Переопределяем значения из переменных окружения
    env_config = load_config_from_env()
    config.update(env_config)
    
    return config

# Пример использования
if __name__ == "__main__":
    # Получаем конфигурацию для разработки
    dev_config = get_config("development")
    print("Development config:", dev_config)
    
    # Получаем конфигурацию для продакшена
    prod_config = get_config("production")
    print("Production config:", prod_config)
    
    # Получаем конфигурацию для тестирования
    test_config = get_config("testing")
    print("Testing config:", test_config) 