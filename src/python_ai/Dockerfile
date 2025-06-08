# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

WORKDIR /app/ai
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libsnappy-dev \
        libffi-dev \
        pkg-config \
    && pip install --no-cache-dir --default-timeout=300 --prefer-binary -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential python3-dev libffi-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
COPY . .
CMD ["python", "main.py"]
