FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p /app/logs /app/data /app/reports

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=info

# Запуск приложения
CMD ["python", "main.py"] 