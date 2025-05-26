# Python Game Server

Серверная часть игры Tetris, реализованная на Python с использованием FastAPI и WebSocket.

## Структура проекта

```
src/python_server/
├── src/
│   ├── main.py              # Основной файл сервера
│   ├── config.py            # Конфигурация
│   ├── exceptions.py        # Исключения
│   ├── utils.py            # Утилиты
│   ├── game/               # Игровая логика
│   │   ├── manager.py      # Менеджер игр
│   │   └── types.py        # Типы данных
│   ├── session/            # Управление сессиями
│   │   └── manager.py      # Менеджер сессий
│   ├── network/            # Сетевой слой
│   │   └── manager.py      # Менеджер сети
│   └── physics/            # Физика
│       └── manager.py      # Менеджер физики
├── tests/                  # Тесты
│   ├── test_game.py
│   ├── test_session.py
│   ├── test_network.py
│   ├── test_physics.py
│   └── test_utils.py
├── Dockerfile             # Конфигурация Docker
└── requirements.txt       # Зависимости Python
```

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите сервер:
```bash
python src/main.py
```

Или используйте Docker:
```bash
docker-compose up python-server
```

## API

### WebSocket Endpoints

- `/ws` - WebSocket соединение для игровых событий

### HTTP Endpoints

- `GET /health` - Проверка состояния сервера

### WebSocket Сообщения

#### Создание игры
```json
{
    "type": "create_game",
    "settings": {
        "game_type": "classic",
        "difficulty": "medium",
        "max_players": 4,
        "time_limit": 300,
        "score_limit": 1000
    }
}
```

#### Присоединение к игре
```json
{
    "type": "join_game",
    "game_id": "uuid",
    "session_id": "uuid"
}
```

#### Выход из игры
```json
{
    "type": "leave_game",
    "session_id": "uuid"
}
```

#### Игровые действия
```json
{
    "type": "game_action",
    "game_id": "uuid",
    "action": "move",
    "direction": "left"
}
```

## Конфигурация

Настройки сервера можно изменить через переменные окружения:

- `SERVER_HOST` - Хост сервера (по умолчанию: "0.0.0.0")
- `SERVER_PORT` - Порт сервера (по умолчанию: 8080)
- `GAME_UPDATE_INTERVAL` - Интервал обновления игры (по умолчанию: 0.016)
- `SESSION_CLEANUP_INTERVAL` - Интервал очистки сессий (по умолчанию: 300)
- `SESSION_HEARTBEAT_INTERVAL` - Интервал heartbeat (по умолчанию: 30)
- `PHYSICS_GRAVITY` - Гравитация (по умолчанию: 9.8)
- `PHYSICS_FRICTION` - Трение (по умолчанию: 0.1)
- `LOG_LEVEL` - Уровень логирования (по умолчанию: "INFO")
- `LOG_FILE` - Файл логов (по умолчанию: "logs/server.log")

## Тестирование

Запустите тесты:
```bash
pytest tests/
```

## Логирование

Сервер использует библиотеку `loguru` для логирования. Логи сохраняются в директорию `logs/`.

## Безопасность

- Все входящие сообщения валидируются
- Используются UUID для идентификации игр и сессий
- Реализована защита от переполнения буфера
- Поддерживается CORS 