# Руководство по развертыванию

## Требования

### Системные требования

- Python 3.10+
- Node.js 18+
- C++ 20
- Docker
- Docker Compose
- PostgreSQL 15+
- Redis 7+

### Зависимости

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

## Подготовка к развертыванию

### Клонирование репозитория

```bash
git clone https://github.com/your-username/tetris.git
cd tetris
```

### Установка зависимостей

```bash
# Python зависимости
pip install -r requirements.txt

# Node.js зависимости
cd src/typescript_client
npm install
cd ../..

# C++ зависимости
cd src/cpp_physics
cmake .
make
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
```

## Развертывание

### Развертывание через Docker

```bash
# Сборка и запуск
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down
```

### Запуск без привилегий (Rootless Docker)

Если при запуске `docker-compose` возникают ошибки вида `operation not permitted`
или проблемы с iptables, можно воспользоваться режимом rootless Docker.

```bash
# Установка пакета rootless Docker (для Ubuntu/Debian)
sudo apt-get install docker-ce-rootless-extras
dockerd-rootless-setuptool.sh install

# Экспорт переменных окружения для текущей сессии
export PATH="$HOME/bin:$PATH"
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"

# Запуск контейнеров
docker compose up --build
```

Подробнее о настройке rootless Docker смотрите в [официальной
документации](https://docs.docker.com/engine/security/rootless/).

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
```

## Конфигурация
Основные настройки находятся в файле `docker-compose.yml`:

```yaml
services:
  python-tools:
    build:
      context: ./src/python_tools
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
      - DB_URL=postgresql://user:password@postgres:5432/tetris
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - tetris_network
```

## Мониторинг

### Метрики

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- StatsD: http://localhost:8125

### Логи

- ELK Stack: http://localhost:5601
- Jaeger: http://localhost:16686

```bash
# Просмотр логов
docker-compose logs -f python-tools

# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats
```

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
pg_dump -U postgres tetris_analytics > backup.sql

# Redis
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup/
```

## Обновление

### Обновление через Docker

```bash
# Остановка контейнеров
docker-compose down

# Обновление кода
git pull

# Пересборка и запуск
docker-compose up --build -d
```

### Обновление вручную

```bash
# Обновление Python зависимостей
pip install -r requirements.txt --upgrade

# Обновление Node.js зависимостей
cd src/typescript_client
npm update
cd ../..

# Пересборка C++
cd src/cpp_physics
cmake .
make clean
make
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
pip install -r requirements.txt

# Откат Node.js зависимостей
cd src/typescript_client
npm ci
cd ../..

# Пересборка C++
cd src/cpp_physics
git checkout .
cmake .
make clean
make
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

# Сканирование кода
bandit -r .
pylint .
npm run security
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
```

### Отладка

```bash
# Python
python -m pdb main.py

# TypeScript
node --inspect main.js

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

# C++
doxygen Doxyfile
```

### Просмотр документации

```bash
# Python
open docs/build/html/index.html

# TypeScript
npm run docs:serve

# C++
open docs/html/index.html
```