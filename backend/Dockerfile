# Backend image — Phase 1
#
# WHY python:3.12-slim: a small, official Python base. "slim" keeps the image lean while still
# having what pip needs for these pure-Python / prebuilt-wheel packages.

FROM python:3.12-slim

# Good Python defaults inside containers:
#   PYTHONDONTWRITEBYTECODE=1 -> don't scatter .pyc files
#   PYTHONUNBUFFERED=1        -> print() shows up immediately in `docker compose logs`
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy ONLY requirements first, then install. WHY: Docker caches this layer, so as long as
# requirements.txt doesn't change, rebuilds skip re-installing everything — much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source into the image so it can run standalone (e.g. on Render/Railway). In local
# development, docker-compose bind-mounts ./backend over /app and overrides the command with
# --reload, so this COPY/CMD are ignored there.
COPY . .

# Production start command. Shell form so ${PORT} (set by hosts like Render) is expanded;
# falls back to 8000. docker-compose overrides this with a --reload command for development.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
