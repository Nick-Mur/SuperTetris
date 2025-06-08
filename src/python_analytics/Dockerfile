FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*
CMD ["python", "-m", "python_analytics.main"] # Assuming main.py or similar entry point 