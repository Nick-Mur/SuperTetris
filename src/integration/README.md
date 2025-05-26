# Интеграция компонентов

## Архитектура

Проект состоит из следующих основных компонентов:

1. **Python (Игровая логика)** - основная логика игры
2. **TypeScript (Клиентская часть)** - пользовательский интерфейс
3. **C++ (Физический движок)** - физика и коллизии
4. **Go (Инструменты разработки)** - утилиты для разработки
5. **Python (Аналитика)** - сбор и анализ данных о игровом процессе

## Механизмы взаимодействия

### Python Игровая логика <-> TypeScript Клиентская часть
- REST API для основных операций
- WebSocket для реального времени
- Файлы: 
  - `/src/python_logic/api/endpoints.py` - Python API endpoints
  - `/src/typescript_client/api/client.ts` - TypeScript API клиент

### Python Игровая логика <-> C++ Физический движок
- FFI (Foreign Function Interface)
- Файлы:
  - `/src/python_logic/physics/bindings.py` - Python bindings
  - `/src/cpp_physics/include/PhysicsEngine.h` - C++ интерфейс

### Python Игровая логика <-> Go Инструменты
- REST API
- Файлы:
  - `/src/python_logic/tools/interface.py` - Python интерфейс
  - `/src/go_tools/api/server.go` - Go API сервер

### Python Аналитика <-> Python Игровая логика
- REST API
- Файлы:
  - `/src/python_analytics/api/endpoints.py` - API endpoints
  - `/src/python_logic/analytics/client.py` - API клиент

## Требования к окружению

- Python 3.10+
- Node.js 18+
- Go 1.21+
- C++ 20
- Docker
- Docker Compose

## Установка и запуск

1. Клонирование репозитория:
```bash
git clone https://github.com/your-username/tetris.git
cd tetris
```

2. Установка зависимостей:
```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости
cd src/typescript_client
npm install
cd ../..

# Go зависимости
cd src/go_tools
go mod download
cd ../..

# C++ зависимости
cd src/cpp_physics
cmake -B build
cmake --build build
cd ../..
```

3. Запуск всех компонентов:
```bash
./start.sh
```

## Тестирование

```bash
# Запуск всех тестов
./system_test.sh

# Или запуск тестов отдельных компонентов
cd src/python_logic && python -m pytest
cd src/typescript_client && npm test
cd src/cpp_physics && ctest
cd src/go_tools && go test ./...
cd src/python_analytics && python -m pytest
```
