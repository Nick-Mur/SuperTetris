# Руководство по тестированию

## Типы тестов

### Unit тесты

#### Python Game Server

```python
# tests/test_game_server.py
import pytest
from src.python_server.game import GameServer

def test_create_session():
    server = GameServer()
    session = server.create_session("player1", "classic", "easy")
    assert session.player_id == "player1"
    assert session.game_mode == "classic"
    assert session.difficulty == "easy"

def test_update_session():
    server = GameServer()
    session = server.create_session("player1", "classic", "easy")
    server.update_session(session.id, {"score": 100, "level": 2})
    assert session.score == 100
    assert session.level == 2
```

#### Python Analytics

```python
# tests/test_analytics.py
import pytest
from src.python_analytics.analytics import Analytics

def test_collect_metrics():
    analytics = Analytics()
    metrics = analytics.collect_metrics("game_session", {"score": 100})
    assert metrics.type == "game_session"
    assert metrics.value == 100

def test_generate_report():
    analytics = Analytics()
    report = analytics.generate_report("daily", {"start_date": "2024-01-01"})
    assert report.type == "daily"
    assert report.parameters["start_date"] == "2024-01-01"
```

#### Python AI

```python
# tests/test_ai.py
import pytest
from src.python_ai.ai import AI

def test_predict_move():
    ai = AI()
    prediction = ai.predict_move({"board": [], "piece": "I"})
    assert prediction in ["left", "right", "rotate", "drop"]

def test_train_model():
    ai = AI()
    model = ai.train_model("reinforcement", {"epochs": 100})
    assert model.type == "reinforcement"
    assert model.parameters["epochs"] == 100
```

#### TypeScript Client

```typescript
// tests/test_client.ts
import { GameClient } from '../src/typescript_client/game';

describe('GameClient', () => {
    let client: GameClient;

    beforeEach(() => {
        client = new GameClient();
    });

    test('should connect to server', async () => {
        await client.connect();
        expect(client.isConnected()).toBe(true);
    });

    test('should send move', async () => {
        await client.connect();
        const response = await client.sendMove('left');
        expect(response.success).toBe(true);
    });
});
```

#### C++ Physics Engine

```cpp
// tests/test_physics.cpp
#include <gtest/gtest.h>
#include "../src/cpp_physics/physics.h"

TEST(PhysicsEngine, CheckCollision) {
    PhysicsEngine engine;
    Piece piece = Piece::I;
    Position pos = {0, 0};
    Board board = Board();
    EXPECT_FALSE(engine.checkCollision(piece, pos, board));
}

TEST(PhysicsEngine, ApplyGravity) {
    PhysicsEngine engine;
    Piece piece = Piece::I;
    Position pos = {0, 0};
    Board board = Board();
    Position newPos = engine.applyGravity(piece, pos, board);
    EXPECT_EQ(newPos.y, 1);
}
```

#### Go Development Tools

```go
// tests/test_tools.go
package tools

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestGenerateCode(t *testing.T) {
    generator := NewCodeGenerator()
    code, err := generator.Generate("template", map[string]interface{}{
        "name": "test",
    })
    assert.NoError(t, err)
    assert.Contains(t, code, "test")
}

func TestValidateData(t *testing.T) {
    validator := NewValidator()
    result, err := validator.Validate("user", map[string]interface{}{
        "name": "test",
    })
    assert.NoError(t, err)
    assert.True(t, result.Valid)
}
```

### Интеграционные тесты

#### Python Game Server + TypeScript Client

```python
# tests/test_integration.py
import pytest
from src.python_server.game import GameServer
from src.typescript_client.game import GameClient

def test_game_flow():
    server = GameServer()
    client = GameClient()
    
    # Подключение
    client.connect()
    assert client.is_connected()
    
    # Создание сессии
    session = server.create_session("player1", "classic", "easy")
    client.join_session(session.id)
    assert client.current_session == session.id
    
    # Игровой процесс
    client.send_move("left")
    state = server.get_game_state(session.id)
    assert state.piece.position.x < 0
```

#### Python Analytics + Python AI

```python
# tests/test_analytics_ai.py
import pytest
from src.python_analytics.analytics import Analytics
from src.python_ai.ai import AI

def test_ai_training_with_analytics():
    analytics = Analytics()
    ai = AI()
    
    # Сбор данных
    metrics = analytics.collect_metrics("game_session", {"score": 100})
    ai.add_training_data(metrics)
    
    # Обучение
    model = ai.train_model("reinforcement", {"epochs": 100})
    assert model.accuracy > 0.8
```

#### C++ Physics Engine + Python Game Server

```python
# tests/test_physics_server.py
import pytest
from src.python_server.game import GameServer
from src.cpp_physics.physics import PhysicsEngine

def test_physics_integration():
    server = GameServer()
    physics = PhysicsEngine()
    
    # Создание сессии
    session = server.create_session("player1", "classic", "easy")
    
    # Проверка физики
    piece = physics.create_piece("I")
    position = physics.get_position(piece)
    board = server.get_board(session.id)
    
    collision = physics.check_collision(piece, position, board)
    assert not collision
```

### End-to-end тесты

```python
# tests/test_e2e.py
import pytest
from src.python_server.game import GameServer
from src.typescript_client.game import GameClient
from src.python_analytics.analytics import Analytics
from src.python_ai.ai import AI
from src.cpp_physics.physics import PhysicsEngine

def test_full_game_flow():
    # Инициализация компонентов
    server = GameServer()
    client = GameClient()
    analytics = Analytics()
    ai = AI()
    physics = PhysicsEngine()
    
    # Подключение
    client.connect()
    assert client.is_connected()
    
    # Создание сессии
    session = server.create_session("player1", "classic", "easy")
    client.join_session(session.id)
    assert client.current_session == session.id
    
    # Игровой процесс
    for _ in range(10):
        # Получение предсказания от ИИ
        prediction = ai.predict_move(server.get_game_state(session.id))
        
        # Отправка хода
        client.send_move(prediction)
        
        # Проверка физики
        piece = physics.create_piece(server.get_current_piece(session.id))
        position = physics.get_position(piece)
        board = server.get_board(session.id)
        collision = physics.check_collision(piece, position, board)
        assert not collision
        
        # Сбор метрик
        metrics = analytics.collect_metrics("game_session", {
            "score": server.get_score(session.id),
            "level": server.get_level(session.id)
        })
        assert metrics.type == "game_session"
    
    # Проверка результатов
    final_score = server.get_score(session.id)
    assert final_score > 0
    
    # Генерация отчета
    report = analytics.generate_report("session", {
        "session_id": session.id
    })
    assert report.type == "session"
```

## Запуск тестов

### Запуск всех тестов

```bash
# Запуск всех тестов
./system_test.sh

# Или запуск тестов отдельных компонентов
cd src/python_server && python -m pytest
cd src/python_analytics && python -m pytest
cd src/python_ai && python -m pytest
cd src/typescript_client && npm test
cd src/cpp_physics && ctest
cd src/go_tools && go test ./...
```

### Запуск конкретных тестов

```bash
# Python
python -m pytest tests/test_game_server.py::test_create_session

# TypeScript
npm test -- -t "should connect to server"

# Go
go test -run TestGenerateCode

# C++
ctest -R "CheckCollision"
```

### Запуск с покрытием

```bash
# Python
python -m pytest --cov=src tests/

# TypeScript
npm test -- --coverage

# Go
go test -cover ./...

# C++
ctest -T Coverage
```

## Отчеты о тестировании

### Генерация отчетов

```bash
# Python
python -m pytest --html=report.html

# TypeScript
npm test -- --coverage --coverageReporters=html

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# C++
ctest -T Coverage
```

### Просмотр отчетов

```bash
# Python
open report.html

# TypeScript
open coverage/lcov-report/index.html

# Go
open coverage.html

# C++
open Testing/Coverage/index.html
```

## Непрерывная интеграция

### GitHub Actions

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest
```

### GitLab CI

```yaml
test:
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - python -m pytest
```

## Отладка тестов

### Логи

```bash
# Просмотр логов
tail -f logs/*.log

# Или просмотр логов отдельных компонентов
tail -f logs/python_server.log
tail -f logs/python_analytics.log
tail -f logs/python_ai.log
tail -f logs/typescript_client.log
tail -f logs/cpp_physics.log
tail -f logs/go_tools.log
```

### Отладка

```bash
# Python
python -m pdb -m pytest tests/test_game_server.py

# TypeScript
node --inspect-brk node_modules/.bin/jest

# Go
dlv test ./...

# C++
gdb ./physics_engine_test
```

## Бенчмарки

### Python

```python
# tests/test_benchmark.py
import pytest
from src.python_server.game import GameServer

def test_game_server_performance(benchmark):
    server = GameServer()
    session = server.create_session("player1", "classic", "easy")
    
    def update_game():
        server.update_session(session.id, {"score": 100})
    
    benchmark(update_game)
```

### TypeScript

```typescript
// tests/test_benchmark.ts
import { GameClient } from '../src/typescript_client/game';

describe('GameClient', () => {
    test('should handle moves quickly', () => {
        const client = new GameClient();
        const start = performance.now();
        
        for (let i = 0; i < 1000; i++) {
            client.sendMove('left');
        }
        
        const end = performance.now();
        expect(end - start).toBeLessThan(1000);
    });
});
```

### Go

```go
// tests/test_benchmark.go
package tools

import (
    "testing"
)

func BenchmarkGenerateCode(b *testing.B) {
    generator := NewCodeGenerator()
    for i := 0; i < b.N; i++ {
        generator.Generate("template", map[string]interface{}{
            "name": "test",
        })
    }
}
```

### C++

```cpp
// tests/test_benchmark.cpp
#include <benchmark/benchmark.h>
#include "../src/cpp_physics/physics.h"

static void BM_CheckCollision(benchmark::State& state) {
    PhysicsEngine engine;
    Piece piece = Piece::I;
    Position pos = {0, 0};
    Board board = Board();
    
    for (auto _ : state) {
        engine.checkCollision(piece, pos, board);
    }
}

BENCHMARK(BM_CheckCollision);
``` 