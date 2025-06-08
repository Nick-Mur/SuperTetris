# Dockerfile для Python игровой логики
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
CMD ["python", "-m", "python_logic.game_logic"] # Assuming game_logic.py is the entry
 