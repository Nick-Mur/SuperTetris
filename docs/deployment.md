# Руководство по развертыванию

## Требования

### Системные требования

- Python 3.10+
- Node.js 18+
- Go 1.21+
- C++ 20
- Docker
- Docker Compose
- PostgreSQL 15+
- Redis 7+
- MongoDB 6+

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

## Подготовка к развертыванию

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

### Настройка баз данных

```bash
# PostgreSQL
psql -U postgres -c "CREATE DATABASE tetris;"
psql -U postgres -c "CREATE USER tetris WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE tetris TO tetris;"

# Redis
redis-cli
> AUTH password
> FLUSHALL

# MongoDB
mongosh
> use tetris
> db.createUser({user: "tetris", pwd: "password", roles: ["readWrite"]})
```

## Развертывание

### Развертывание через Docker

```bash
# Сборка образов
docker-compose build

# Запуск контейнеров
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### Развертывание вручную

```bash
# Запуск Python Game Server
cd src/python_server
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Запуск Python Analytics
cd src/python_analytics
python -m uvicorn main:app --host 0.0.0.0 --port 8001

# Запуск Python AI
cd src/python_ai
python -m uvicorn main:app --host 0.0.0.0 --port 8002

# Запуск TypeScript Client
cd src/typescript_client
npm run build
npm run start

# Запуск C++ Physics Engine
cd src/cpp_physics
./build/physics_engine

# Запуск Go Development Tools
cd src/go_tools
go run main.go
```

## Мониторинг

### Метрики

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- StatsD: http://localhost:8125

### Логи

- ELK Stack: http://localhost:5601
- Jaeger: http://localhost:16686

## Масштабирование

### Горизонтальное масштабирование

```bash
# Масштабирование Python Game Server
docker-compose up -d --scale python_server=3

# Масштабирование Python Analytics
docker-compose up -d --scale python_analytics=2

# Масштабирование Python AI
docker-compose up -d --scale python_ai=2
```

### Вертикальное масштабирование

```bash
# Настройка ресурсов в docker-compose.yml
services:
  python_server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Резервное копирование

### База данных

```bash
# PostgreSQL
pg_dump -U tetris tetris > backup.sql

# MongoDB
mongodump --db tetris --out backup

# Redis
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup.rdb
```

### Логи

```bash
# Архивация логов
tar -czf logs.tar.gz logs/

# Ротация логов
logrotate /etc/logrotate.d/tetris
```

## Обновление

### Обновление через Docker

```bash
# Получение обновлений
git pull

# Пересборка образов
docker-compose build

# Перезапуск контейнеров
docker-compose up -d
```

### Обновление вручную

```bash
# Обновление Python зависимостей
python -m pip install -r requirements.txt --upgrade

# Обновление Node.js зависимостей
cd src/typescript_client
npm update
cd ../..

# Обновление Go зависимостей
cd src/go_tools
go get -u ./...
cd ../..

# Пересборка C++
cd src/cpp_physics
cmake -B build
cmake --build build
cd ../..
```

## Откат

### Откат через Docker

```bash
# Откат к предыдущей версии
git checkout v1.0.0
docker-compose down
docker-compose up -d
```

### Откат вручную

```bash
# Откат Python зависимостей
python -m pip install -r requirements.txt --upgrade --force-reinstall

# Откат Node.js зависимостей
cd src/typescript_client
npm ci
cd ../..

# Откат Go зависимостей
cd src/go_tools
go mod tidy
cd ../..

# Пересборка C++
cd src/cpp_physics
cmake -B build
cmake --build build
cd ../..
```

## Безопасность

### SSL/TLS

```bash
# Генерация сертификатов
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout private.key -out certificate.crt

# Настройка Nginx
server {
    listen 443 ssl;
    server_name tetris.example.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

### Брандмауэр

```bash
# Настройка UFW
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 8001/tcp
ufw allow 8002/tcp
ufw enable
```

### Мониторинг безопасности

```bash
# Проверка зависимостей
safety check
npm audit
go list -json -m all | nancy

# Сканирование кода
bandit -r .
pylint .
npm run security
gosec ./...
cppcheck .
```

## Устранение неполадок

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

### Мониторинг ресурсов

```bash
# CPU и память
top
htop

# Диск
df -h
du -sh *

# Сеть
netstat -tulpn
iftop
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