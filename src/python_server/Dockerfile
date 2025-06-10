FROM python:3.11-slim

WORKDIR /app
COPY . /app/python_server
RUN pip install --no-cache-dir --default-timeout=100 -r python_server/requirements.txt
CMD ["python", "-m", "python_server.src.main"] 