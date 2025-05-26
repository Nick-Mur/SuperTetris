class GameError(Exception):
    """Базовый класс для всех игровых ошибок"""
    pass

class GameNotFoundError(GameError):
    """Игра не найдена"""
    pass

class GameAlreadyExistsError(GameError):
    """Игра уже существует"""
    pass

class PlayerNotFoundError(GameError):
    """Игрок не найден"""
    pass

class SessionNotFoundError(GameError):
    """Сессия не найдена"""
    pass

class InvalidGameSettingsError(GameError):
    """Некорректные настройки игры"""
    pass

class GameFullError(GameError):
    """Игра заполнена"""
    pass

class GameNotRunningError(GameError):
    """Игра не запущена"""
    pass

class InvalidActionError(GameError):
    """Некорректное действие"""
    pass

class NetworkError(GameError):
    """Ошибка сети"""
    pass

class PhysicsError(GameError):
    """Ошибка физики"""
    pass 