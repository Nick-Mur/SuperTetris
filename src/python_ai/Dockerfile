# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /app/ai
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
