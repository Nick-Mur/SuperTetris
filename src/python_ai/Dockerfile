# Dockerfile для Python AI сервиса
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
# Предполагается наличие requirements.txt в корневой директории проекта
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
# Предполагается, что код находится в src/python_ai
COPY . .

# Создание необходимых директорий, указанных в volumes docker-compose.yml
RUN mkdir -p /app/logs /app/models /app/data

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=info

# Запуск приложения
# Замените 'src/main.py' на фактический файл точки входа, если он отличается
CMD ["python", "src/main.py"] 