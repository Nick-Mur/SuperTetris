FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p data/{levels,sessions,analytics,profiles,reports}

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Открытие порта
EXPOSE 8000

# Запуск приложения
CMD ["python", "-m", "python_tools.main"] 