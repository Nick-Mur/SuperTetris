FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/logs /app/data

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Добавляем common_utils в PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Запуск сервера
CMD ["python", "src/main.py"] 