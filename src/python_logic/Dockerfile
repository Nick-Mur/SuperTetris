# Dockerfile для Python игровой логики
FROM python:3.11-slim

WORKDIR /app

# Копируем общие утилиты
COPY src/common_utils /app/common_utils

# Копируем код логики
COPY src/python_logic /app/logic

# Устанавливаем зависимости
COPY src/python_logic/requirements.txt .
RUN pip install -r requirements.txt

# Добавляем common_utils в PYTHONPATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Запускаем логику
CMD ["python", "logic/main.py"]
