# Dockerfile для Python игровой логики
FROM python:3.11-slim

WORKDIR /app
COPY . /app/python_logic
RUN pip install --no-cache-dir --default-timeout=100 -r python_logic/requirements.txt
CMD python -m python_logic.game_logic
 