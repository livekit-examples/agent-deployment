FROM --platform=linux/arm64 python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from livekit.plugins.silero import VAD; VAD.load()"

COPY agent.py kvs_turn.py .env ./

EXPOSE 8080

CMD ["python", "agent.py", "start"]
