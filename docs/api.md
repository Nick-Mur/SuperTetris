# API Документация

## Python Game Server API

### REST API

#### Игровые сессии

##### Создание сессии
```http
POST /api/game/sessions
Content-Type: application/json

{
    "player_id": "string",
    "game_mode": "string",
    "difficulty": "string"
}
```

##### Получение сессии
```http
GET /api/game/sessions/{session_id}
```

##### Обновление сессии
```http
PUT /api/game/sessions/{session_id}
Content-Type: application/json

{
    "state": "string",
    "score": "number",
    "level": "number"
}
```

##### Удаление сессии
```http
DELETE /api/game/sessions/{session_id}
```

#### Игровая логика

##### Получение состояния игры
```http
GET /api/game/state/{session_id}
```

##### Обновление состояния игры
```http
PUT /api/game/state/{session_id}
Content-Type: application/json

{
    "board": "array",
    "current_piece": "object",
    "next_piece": "object"
}
```

##### Проверка столкновений
```http
POST /api/game/collisions
Content-Type: application/json

{
    "piece": "object",
    "position": "object",
    "board": "array"
}
```

### WebSocket API

#### Подключение
```javascript
const ws = new WebSocket('ws://server/game');
```

#### События

##### Игровые события
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'GAME_STATE':
            // Обработка состояния игры
            break;
        case 'PIECE_MOVED':
            // Обработка движения фигуры
            break;
        case 'LINE_CLEARED':
            // Обработка очистки линии
            break;
        case 'GAME_OVER':
            // Обработка окончания игры
            break;
    }
};
```

##### Отправка событий
```javascript
ws.send(JSON.stringify({
    type: 'MOVE_PIECE',
    data: {
        direction: 'left',
        rotation: 0
    }
}));
```

## Python Analytics API

### REST API

#### Метрики

##### Получение метрик
```http
GET /api/analytics/metrics
Query Parameters:
    - start_time: string
    - end_time: string
    - metric_type: string
```

##### Добавление метрики
```http
POST /api/analytics/metrics
Content-Type: application/json

{
    "type": "string",
    "value": "number",
    "timestamp": "string",
    "tags": "object"
}
```

#### Отчеты

##### Генерация отчета
```http
POST /api/analytics/reports
Content-Type: application/json

{
    "type": "string",
    "parameters": "object",
    "format": "string"
}
```

##### Получение отчета
```http
GET /api/analytics/reports/{report_id}
```

### WebSocket API

#### Подключение
```javascript
const ws = new WebSocket('ws://server/analytics');
```

#### События

##### Метрики в реальном времени
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'METRIC_UPDATE':
            // Обработка обновления метрики
            break;
        case 'ALERT':
            // Обработка оповещения
            break;
    }
};
```

## Python AI API

### REST API

#### Предсказания

##### Получение предсказания
```http
POST /api/ai/predict
Content-Type: application/json

{
    "game_state": "object",
    "player_id": "string",
    "model_type": "string"
}
```

##### Обучение модели
```http
POST /api/ai/train
Content-Type: application/json

{
    "model_type": "string",
    "parameters": "object",
    "data": "array"
}
```

#### Модели

##### Получение списка моделей
```http
GET /api/ai/models
```

##### Получение модели
```http
GET /api/ai/models/{model_id}
```

##### Обновление модели
```http
PUT /api/ai/models/{model_id}
Content-Type: application/json

{
    "parameters": "object",
    "version": "string"
}
```

### WebSocket API

#### Подключение
```javascript
const ws = new WebSocket('ws://server/ai');
```

#### События

##### Предсказания в реальном времени
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'PREDICTION':
            // Обработка предсказания
            break;
        case 'MODEL_UPDATE':
            // Обработка обновления модели
            break;
    }
};
```

## C++ Physics Engine API

### FFI API

#### Инициализация
```python
from ctypes import cdll, c_void_p, c_int, c_float, POINTER, Structure

class Vector2(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float)
    ]

class PhysicsEngine:
    def __init__(self):
        self.lib = cdll.LoadLibrary("./physics_engine.so")
        self.engine = self.lib.create_physics_engine()
```

#### Физические расчеты

##### Расчет столкновений
```python
def check_collision(self, piece, position, board):
    result = self.lib.check_collision(
        self.engine,
        piece,
        position,
        board
    )
    return bool(result)
```

##### Расчет гравитации
```python
def apply_gravity(self, piece, board):
    result = self.lib.apply_gravity(
        self.engine,
        piece,
        board
    )
    return Vector2(result.x, result.y)
```

## Go Development Tools API

### REST API

#### Генерация кода

##### Генерация кода
```http
POST /api/tools/generate
Content-Type: application/json

{
    "type": "string",
    "template": "string",
    "parameters": "object"
}
```

##### Получение шаблонов
```http
GET /api/tools/templates
```

#### Валидация

##### Валидация данных
```http
POST /api/tools/validate
Content-Type: application/json

{
    "type": "string",
    "data": "object",
    "rules": "array"
}
```

##### Получение правил
```http
GET /api/tools/rules
```

### WebSocket API

#### Подключение
```javascript
const ws = new WebSocket('ws://server/tools');
```

#### События

##### Обновления в реальном времени
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
        case 'VALIDATION_RESULT':
            // Обработка результата валидации
            break;
        case 'GENERATION_PROGRESS':
            // Обработка прогресса генерации
            break;
    }
};
``` 