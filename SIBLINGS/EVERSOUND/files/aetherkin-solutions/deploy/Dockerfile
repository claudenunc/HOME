# AetherKin service container
# Built from AetherKin repo root (context: ../..)

FROM python:3.11-slim

WORKDIR /app

# System deps for some optional packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy AetherKin source
COPY . /app/

# Install
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -e .

# AetherKin data lives in mounted volumes
RUN mkdir -p /app/family /app/data /app/.aetherkin

# Expose gateway port (must match AETHERKIN_PORT env)
EXPOSE 7788

# Default command — the gateway HTTP server
# TODO: add gateway/server.py entrypoint that wraps Gateway() in FastAPI
CMD ["python", "-m", "gateway.server"]
