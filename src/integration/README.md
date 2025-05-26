# Интеграция компонентов Tetris с элементами Tricky Towers

Этот документ описывает интеграцию между различными компонентами многоязычной архитектуры игры Tetris с элементами Tricky Towers.

## Обзор интеграции

Наша архитектура использует 7 различных языков программирования, каждый из которых отвечает за определенный аспект игры:

1. **C++ (Физический движок)** - обеспечивает реалистичную физику блоков
2. **Rust (Серверная часть)** - координирует все компоненты и обрабатывает сетевые взаимодействия
3. **Python (Игровая логика)** - реализует правила игры и механики
4. **TypeScript/JavaScript (Клиентская часть)** - обеспечивает пользовательский интерфейс
5. **Julia (Искусственный интеллект)** - реализует ИИ противников
6. **Go (Инструменты разработки)** - предоставляет инструменты для создания уровней и отладки
7. **Scala (Аналитика)** - собирает и анализирует данные о игровом процессе

## Механизмы межъязыкового взаимодействия

Для обеспечения бесшовной интеграции между компонентами используются следующие механизмы:

### 1. FFI (Foreign Function Interface)

FFI используется для прямого вызова функций между языками, особенно для взаимодействия с низкоуровневыми компонентами.

**Примеры использования:**
- Rust вызывает функции C++ физического движка
- Python вызывает функции Rust серверной части
- Julia вызывает функции C++ для физической симуляции

### 2. REST API

REST API используется для HTTP-взаимодействия между компонентами, особенно для клиент-серверного взаимодействия.

**Примеры использования:**
- TypeScript клиент взаимодействует с Rust сервером
- Go инструменты взаимодействуют с Rust сервером
- Внешние сервисы взаимодействуют с игровой системой

### 3. WebSocket

WebSocket используется для двунаправленной связи в реальном времени.

**Примеры использования:**
- Обновление состояния игры между сервером и клиентом
- Многопользовательская синхронизация
- Обновления ИИ в реальном времени

### 4. Message Queue

Очереди сообщений используются для асинхронного взаимодействия между компонентами.

**Примеры использования:**
- Отправка событий от игровой логики к аналитике
- Обработка действий игрока
- Распределение задач между компонентами

### 5. Shared Memory

Разделяемая память используется для высокопроизводительного обмена данными между компонентами.

**Примеры использования:**
- Обмен данными между физическим движком и игровой логикой
- Обмен данными между ИИ и сервером
- Кэширование часто используемых данных

## Схема интеграции

```
+-------------------+      FFI      +-------------------+
| C++ Physics Engine |<------------->| Rust Game Server  |
+-------------------+              +-------------------+
         ^                                  ^
         | FFI                              | REST/WebSocket
         v                                  v
+-------------------+      FFI      +-------------------+
| Python Game Logic |<------------->| TypeScript Client |
+-------------------+              +-------------------+
         ^                                  ^
         | Message Queue                    | WebSocket
         v                                  v
+-------------------+      REST     +-------------------+
| Julia AI System   |<------------->| Go Dev Tools      |
+-------------------+              +-------------------+
         ^                                  ^
         | Message Queue                    | REST
         v                                  v
+-------------------+      REST     +-------------------+
| Scala Analytics   |<------------->| External Services |
+-------------------+              +-------------------+
```

## Детали интеграции по компонентам

### C++ Физический движок <-> Rust Серверная часть

**Механизм:** FFI через динамическую библиотеку

**Файлы интеграции:**
- `/src/cpp_physics/include/FFIInterface.h` - C++ заголовочный файл с экспортируемыми функциями
- `/src/cpp_physics/FFIInterface.cpp` - C++ реализация экспортируемых функций
- `/src/rust_server/src/ffi.rs` - Rust модуль для вызова C++ функций

**Пример использования:**
```rust
// В Rust коде
extern "C" {
    fn physics_simulate_step(dt: f32) -> bool;
    fn physics_apply_force(entity_id: i32, force_x: f32, force_y: f32) -> bool;
}

// Вызов C++ функции из Rust
unsafe {
    physics_simulate_step(0.016);  // 60 FPS
}
```

### Rust Серверная часть <-> Python Игровая логика

**Механизм:** FFI через ctypes и REST API

**Файлы интеграции:**
- `/src/rust_server/src/python_bridge.rs` - Rust модуль для взаимодействия с Python
- `/src/python_logic/rust_interface.py` - Python модуль для взаимодействия с Rust

**Пример использования:**
```python
# В Python коде
import ctypes
from rust_interface import RustServer

# Инициализация интерфейса с Rust
server = RustServer()

# Вызов Rust функции
result = server.update_game_state(game_id, player_id, action_type, action_data)
```

### Python Игровая логика <-> TypeScript Клиентская часть

**Механизм:** WebSocket через Rust сервер

**Файлы интеграции:**
- `/src/python_logic/websocket_handler.py` - Python обработчик WebSocket сообщений
- `/src/typescript_client/src/api/GameSocket.ts` - TypeScript класс для WebSocket взаимодействия

**Пример использования:**
```typescript
// В TypeScript коде
import { GameSocket } from '../api/GameSocket';

const socket = new GameSocket('ws://game-server.com/ws');

// Отправка действия игрока
socket.sendPlayerAction({
  type: 'MOVE_BLOCK',
  direction: 'LEFT',
  playerId: currentPlayer.id
});

// Получение обновлений состояния игры
socket.onGameStateUpdate((state) => {
  updateGameView(state);
});
```

### Julia ИИ <-> Rust Серверная часть

**Механизм:** FFI и Message Queue

**Файлы интеграции:**
- `/src/julia_ai/rust_bridge.jl` - Julia модуль для взаимодействия с Rust
- `/src/rust_server/src/ai_interface.rs` - Rust модуль для взаимодействия с Julia AI

**Пример использования:**
```julia
# В Julia коде
module RustBridge

using Libdl

const rust_lib = Libdl.dlopen("libtetris_server.so")
const get_game_state = Libdl.dlsym(rust_lib, :get_game_state)
const send_ai_action = Libdl.dlsym(rust_lib, :send_ai_action)

function fetch_game_state(game_id::String)
    # Вызов Rust функции для получения состояния игры
    result_ptr = ccall(get_game_state, Ptr{UInt8}, (Cstring,), game_id)
    result = unsafe_string(result_ptr)
    return JSON.parse(result)
end

function submit_action(game_id::String, action_type::String, action_data::Dict)
    # Отправка действия ИИ в Rust сервер
    action_json = JSON.json(action_data)
    ccall(send_ai_action, Bool, (Cstring, Cstring, Cstring), 
          game_id, action_type, action_json)
end

end # module
```

### Go Инструменты разработки <-> Rust Серверная часть

**Механизм:** REST API

**Файлы интеграции:**
- `/src/go_tools/api/server_client.go` - Go клиент для взаимодействия с Rust сервером
- `/src/rust_server/src/dev_api.rs` - Rust модуль с API для инструментов разработки

**Пример использования:**
```go
// В Go коде
package main

import (
    "github.com/tetris-towers/dev-tools/api"
)

func main() {
    client := api.NewServerClient("http://localhost:8080")
    
    // Получение списка активных игр
    games, err := client.GetActiveGames()
    if err != nil {
        log.Fatalf("Failed to get active games: %v", err)
    }
    
    // Создание нового уровня
    level := &api.Level{
        Name: "Test Level",
        Difficulty: "Medium",
        Blocks: []api.Block{
            {Type: "L", InitialX: 5, InitialY: 0},
            {Type: "I", InitialX: 2, InitialY: 3},
        },
    }
    
    levelID, err := client.CreateLevel(level)
    if err != nil {
        log.Fatalf("Failed to create level: %v", err)
    }
    
    fmt.Printf("Created level with ID: %s\n", levelID)
}
```

### Scala Аналитика <-> Rust Серверная часть

**Механизм:** Message Queue и REST API

**Файлы интеграции:**
- `/src/scala_analytics/server_interface.scala` - Scala интерфейс для взаимодействия с сервером
- `/src/rust_server/src/analytics_api.rs` - Rust модуль с API для аналитики

**Пример использования:**
```scala
// В Scala коде
import com.tetristowers.analytics.ServerInterface

val server = new ServerInterface("http://game-server.com/api")

// Получение игровых событий
val events = server.fetchGameEvents(startTime, endTime)

// Анализ событий
val results = gameplayAnalyzer.analyze(events)

// Отправка рекомендаций обратно на сервер
server.sendBalanceRecommendations(results.balanceRecommendations)
```

## Протоколы и форматы данных

### REST API

**Базовый URL:** `http://server:8080/api/v1`

**Основные эндпоинты:**
- `GET /games` - Получение списка игр
- `GET /games/{id}` - Получение информации о конкретной игре
- `POST /games` - Создание новой игры
- `PUT /games/{id}/action` - Выполнение действия в игре
- `GET /players` - Получение списка игроков
- `GET /analytics/summary` - Получение сводной аналитики
- `GET /levels` - Получение списка уровней
- `POST /levels` - Создание нового уровня

**Формат данных:** JSON

### WebSocket

**URL:** `ws://server:8080/ws`

**События:**
- `game_state_update` - Обновление состояния игры
- `player_action` - Действие игрока
- `block_placed` - Блок размещен
- `lines_cleared` - Линии очищены
- `spell_cast` - Заклинание использовано
- `game_over` - Игра окончена

**Формат данных:** JSON

### Message Queue

**Используемая технология:** RabbitMQ

**Основные очереди:**
- `game_events` - События игры для аналитики
- `player_actions` - Действия игроков
- `ai_decisions` - Решения ИИ
- `system_metrics` - Метрики производительности системы

**Формат данных:** JSON

## Запуск и тестирование интеграции

### Предварительные требования

- CMake 3.15+
- Rust 1.50+
- Python 3.8+
- Node.js 14+
- Julia 1.6+
- Go 1.16+
- Scala 2.13+ с SBT
- RabbitMQ

### Сборка и запуск

1. Сборка C++ физического движка:
   ```bash
   cd src/cpp_physics
   mkdir -p build && cd build
   cmake ..
   make
   ```

2. Сборка Rust серверной части:
   ```bash
   cd src/rust_server
   cargo build --release
   ```

3. Установка зависимостей Python:
   ```bash
   cd src/python_logic
   pip install -r requirements.txt
   ```

4. Сборка TypeScript клиента:
   ```bash
   cd src/typescript_client
   npm install
   npm run build
   ```

5. Установка зависимостей Julia:
   ```bash
   cd src/julia_ai
   julia -e 'using Pkg; Pkg.activate("."); Pkg.instantiate()'
   ```

6. Сборка Go инструментов:
   ```bash
   cd src/go_tools
   go build
   ```

7. Сборка Scala аналитики:
   ```bash
   cd src/scala_analytics
   sbt compile
   ```

8. Запуск интеграционных тестов:
   ```bash
   cd tests
   ./run_integration_tests.sh
   ```

## Диагностика проблем интеграции

### Общие проблемы и решения

1. **Проблема:** Ошибка загрузки динамической библиотеки
   **Решение:** Убедитесь, что путь к библиотеке правильный и библиотека собрана для нужной платформы

2. **Проблема:** Ошибки сериализации/десериализации JSON
   **Решение:** Проверьте соответствие форматов данных между компонентами

3. **Проблема:** Таймауты в сетевых запросах
   **Решение:** Увеличьте таймауты и проверьте доступность сервера

4. **Проблема:** Ошибки в FFI вызовах
   **Решение:** Проверьте соответствие типов данных и сигнатур функций

### Логирование

Все компоненты используют унифицированную систему логирования, которая сохраняет логи в директории `/logs`:

- `/logs/physics.log` - Логи физического движка
- `/logs/server.log` - Логи серверной части
- `/logs/game_logic.log` - Логи игровой логики
- `/logs/client.log` - Логи клиентской части
- `/logs/ai.log` - Логи системы ИИ
- `/logs/tools.log` - Логи инструментов разработки
- `/logs/analytics.log` - Логи системы аналитики
- `/logs/integration.log` - Логи интеграционных процессов

### Мониторинг

Для мониторинга состояния компонентов используется панель мониторинга, доступная по адресу `http://server:8081/dashboard`.

## Заключение

Интеграция между компонентами является ключевым аспектом нашей многоязычной архитектуры. Правильное использование механизмов межъязыкового взаимодействия обеспечивает бесшовную работу всей системы и позволяет каждому языку программирования проявить свои сильные стороны в соответствующей области.
