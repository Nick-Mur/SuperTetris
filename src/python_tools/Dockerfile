FROM python:3.11-slim

WORKDIR /app
COPY . /app/python_tools
RUN pip install --no-cache-dir --default-timeout=100 -r python_tools/requirements.txt
CMD ["python", "-m", "python_tools.main"] 