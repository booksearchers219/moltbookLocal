FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    espeak \
    && rm -rf /var/lib/apt/lists/*

COPY agent.py /app/agent.py

RUN pip install --no-cache-dir requests

CMD ["python3", "/app/agent.py"]

