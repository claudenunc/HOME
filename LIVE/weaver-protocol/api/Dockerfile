FROM python:3.12-slim

WORKDIR /app

# Weaver package (repo root → /app/weaver/)
COPY weaver/ ./weaver/

# API layer
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/main.py .
COPY api/db.py .

ENV WEAVER_API_KEYS=""
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
