# Dockerfile для Python игровой логики
FROM python:3.11-slim

WORKDIR /app

# Установка необходимых зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Запуск сервиса
CMD ["python", "game_logic.py"]
