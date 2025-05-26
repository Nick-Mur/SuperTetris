# Руководство по разработке

## Требования

### Системные требования

- Python 3.10+
- Node.js 18+
- Go 1.21+
- C++ 20
- Docker
- Docker Compose

### Зависимости

- Python зависимости: `requirements.txt`
- Node.js зависимости: `package.json`
- Go зависимости: `go.mod`
- C++ зависимости: `CMakeLists.txt`

## Исключенные файлы (.gitignore)

В репозиторий не включены следующие файлы и директории:

1. **Python-специфичные файлы**:
   - Кэш Python (`__pycache__/`, `*.pyc`, `*.pyo`)
   - Файлы сборки и дистрибутивы
   - Файлы тестового покрытия

2. **Виртуальные окружения**:
   - `venv/`, `env/`, `.venv`
   - Файлы конфигурации окружения (`.env`)

3. **IDE и редакторы**:
   - `.idea/` (PyCharm)
   - `.vscode/` (Visual Studio Code)
   - Временные файлы редакторов

4. **Логи и отладочная информация**:
   - Директория `logs/`
   - Все файлы логов (`*.log`)

5. **Docker**:
   - Временные файлы Docker
   - Файлы переопределения docker-compose

6. **Данные и исследования**:
   - Директория `research/data/`
   - Файлы данных (`.csv`, `.xlsx`, `.db`)

7. **Системные файлы**:
   - `.DS_Store` (macOS)
   - `Thumbs.db` (Windows)
   - `desktop.ini` (Windows)

## Установка

### Клонирование репозитория

```bash
git clone https://github.com/your-username/tetris.git
cd tetris
```

### Установка зависимостей

```bash
# Python зависимости
python -m pip install -r requirements.txt

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

### Настройка окружения

```bash
# Копирование конфигурационных файлов
cp .env.example .env
cp src/python_server/.env.example src/python_server/.env
cp src/python_analytics/.env.example src/python_analytics/.env
cp src/python_ai/.env.example src/python_ai/.env
cp src/typescript_client/.env.example src/typescript_client/.env
```

## Разработка

### Запуск в режиме разработки

```bash
# Запуск всех компонентов
./start.sh

# Или запуск отдельных компонентов
cd src/python_server && python -m uvicorn main:app --reload
cd src/python_analytics && python -m uvicorn main:app --reload
cd src/python_ai && python -m uvicorn main:app --reload
cd src/typescript_client && npm run dev
cd src/cpp_physics && ./build/physics_engine
cd src/go_tools && go run main.go
```

### Тестирование

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

### Линтинг и форматирование

```bash
# Python
black .
isort .
flake8 .
mypy .

# TypeScript
cd src/typescript_client
npm run lint
npm run format
cd ../..

# Go
cd src/go_tools
go fmt ./...
go vet ./...
cd ../..

# C++
cd src/cpp_physics
clang-format -i src/**/*.{h,cpp}
cd ../..
```

## Структура проекта

```
tetris/
├── src/
│   ├── python_server/      # Python Game Server
│   ├── python_analytics/   # Python Analytics
│   ├── python_ai/         # Python AI
│   ├── typescript_client/ # TypeScript Client
│   ├── cpp_physics/      # C++ Physics Engine
│   └── go_tools/         # Go Development Tools
├── tests/                # Тесты
├── docs/                # Документация
├── scripts/             # Скрипты
├── research/            # Исследования
├── build/              # Сборка
└── logs/               # Логи
```

## Коммиты

### Правила именования коммитов

- `feat:` - новая функциональность
- `fix:` - исправление ошибок
- `docs:` - изменения в документации
- `style:` - форматирование кода
- `refactor:` - рефакторинг кода
- `test:` - добавление тестов
- `chore:` - обновление зависимостей

### Примеры коммитов

```
feat: add new game mode
fix: resolve physics collision bug
docs: update API documentation
style: format Python code
refactor: improve game logic
test: add integration tests
chore: update dependencies
```

## Пулл-реквесты

### Правила создания пулл-реквестов

1. Создайте ветку от `main`
2. Внесите изменения
3. Напишите тесты
4. Обновите документацию
5. Создайте пулл-реквест

### Шаблон пулл-реквеста

```markdown
## Описание
[Опишите изменения]

## Тип изменений
- [ ] Новая функциональность
- [ ] Исправление ошибок
- [ ] Изменения в документации
- [ ] Форматирование кода
- [ ] Рефакторинг кода
- [ ] Добавление тестов
- [ ] Обновление зависимостей

## Тесты
- [ ] Unit тесты
- [ ] Интеграционные тесты
- [ ] End-to-end тесты

## Документация
- [ ] API документация
- [ ] Документация по архитектуре
- [ ] Руководство по разработке
- [ ] Руководство по развертыванию
- [ ] Руководство пользователя

## Скриншоты
[Добавьте скриншоты, если применимо]

## Чеклист
- [ ] Код соответствует стилю
- [ ] Тесты проходят
- [ ] Документация обновлена
- [ ] Изменения протестированы
```

## Развертывание

### Подготовка к развертыванию

```bash
# Сборка всех компонентов
./build.sh

# Проверка всех тестов
./system_test.sh

# Проверка линтера
./lint.sh
```

### Развертывание

```bash
# Развертывание через Docker
docker-compose up -d

# Или развертывание вручную
./deploy.sh
```

## Мониторинг

### Метрики

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- StatsD: http://localhost:8125

### Логи

- ELK Stack: http://localhost:5601
- Jaeger: http://localhost:16686

## Отладка

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
python -m pdb main.py

# TypeScript
node --inspect main.js

# Go
dlv debug main.go

# C++
gdb ./physics_engine
```

## Безопасность

### Проверка безопасности

```bash
# Проверка зависимостей
safety check
npm audit
go list -json -m all | nancy
```

### Сканирование кода

```bash
# Python
bandit -r .
pylint .

# TypeScript
npm run security

# Go
gosec ./...

# C++
cppcheck .
```

## Производительность

### Профилирование

```bash
# Python
python -m cProfile main.py

# TypeScript
node --prof main.js

# Go
go tool pprof main.go

# C++
gprof ./physics_engine
```

### Бенчмарки

```bash
# Python
python -m pytest --benchmark-only

# TypeScript
npm run benchmark

# Go
go test -bench=.

# C++
./physics_engine --benchmark
```

## Документация

### Генерация документации

```bash
# Python
sphinx-build -b html docs/source docs/build/html

# TypeScript
npm run docs

# Go
godoc -http=:6060

# C++
doxygen Doxyfile
```

### Просмотр документации

```bash
# Python
open docs/build/html/index.html

# TypeScript
npm run docs:serve

# Go
open http://localhost:6060

# C++
open docs/html/index.html
``` 