FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
CMD ["python", "-m", "python_analytics.main"] # Assuming main.py or similar entry point 