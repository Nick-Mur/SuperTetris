# Руководство по разработке

## Требования к окружению

- Python 3.10+
- Node.js 18+
- C++ 20
- Docker
- Docker Compose
- PostgreSQL 15+
- Redis 7+

## Зависимости

- Python зависимости: `requirements.txt`
- Node.js зависимости: `package.json`
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

1. Клонировать репозиторий
2. Установить зависимости:
```bash
   # Python
pip install -r requirements.txt

   # Node.js
cd src/typescript_client
npm install
   
   # C++
   cd src/cpp_physics
   cmake .
   make
```

## Разработка

### Форматирование кода

```bash
# Python
black .
isort .

# TypeScript
cd src/typescript_client
npm run format

# C++
cd src/cpp_physics
clang-format -i *.cpp *.h
```

### Линтинг

```bash
# Python
flake8
pylint .

# TypeScript
cd src/typescript_client
npm run lint

# C++
cd src/cpp_physics
cppcheck .
```

### Тестирование

```bash
# Python
pytest

# TypeScript
cd src/typescript_client
npm test

# C++
cd src/cpp_physics
ctest
```

### Мониторинг

```bash
# Логи
tail -f logs/python_server.log
tail -f logs/python_logic.log
tail -f logs/typescript_client.log
tail -f logs/python_analytics.log
tail -f logs/python_ai.log
tail -f logs/python_tools.log

# Метрики
http://localhost:9090  # Prometheus
http://localhost:3000  # Grafana
```

### Отладка

```bash
# Python
python -m pdb main.py

# TypeScript
node --inspect main.js

# C++
gdb ./main
```

### Безопасность

```bash
# Сканирование уязвимостей
safety check
npm audit
cppcheck .

# Сканирование кода
bandit -r .
pylint .
npm run security
cppcheck .
```

### Профилирование

```bash
# Python
python -m cProfile main.py

# TypeScript
node --prof main.js

# C++
gprof ./main
```

### Бенчмарки

```bash
# Python
pytest --benchmark-only

# TypeScript
npm run benchmark

# C++
./benchmark
```

### Документация

```bash
# Python
pydoc -p 8080

# TypeScript
npm run docs

# C++
doxygen Doxyfile
```

### Просмотр документации

```bash
# Python
open http://localhost:8080

# TypeScript
npm run docs:serve

# C++
open docs/html/index.html
```

## Структура проекта

```
tetris/
├── src/
│   ├── python_tools/        # Инструменты разработки на Python
│   ├── python_logic/        # Игровая логика на Python
│   ├── python_analytics/    # Аналитика на Python
│   ├── python_ai/          # ИИ на Python
│   ├── typescript_client/   # Клиент на TypeScript
│   ├── cpp_physics/        # Физический движок на C++
│   └── common_utils/       # Общие утилиты
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