# Multi-stage Dockerfile for ABYSS SMS
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH \
    FLASK_ENV=production \
    PORT=20168 \
    HOST=0.0.0.0

EXPOSE 20168

CMD ["gunicorn", "--bind", "0.0.0.0:20168", "--workers", "4", "--threads", "2", "wsgi:app"]
