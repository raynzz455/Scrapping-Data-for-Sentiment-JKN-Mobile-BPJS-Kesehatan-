# ──────────────────────────────────────────────────────────
#  JKN Sentiment — FastAPI Dockerfile
#  Optimasi: slim base image, uv untuk install cepat,
#  non-root user untuk keamanan.
# ──────────────────────────────────────────────────────────
FROM python:3.11-slim

# Install uv (package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files dulu (agar layer ini di-cache kalau code berubah)
COPY pyproject.toml ./
COPY uv.lock ./

# Install dependencies ke dalam .venv
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code
COPY app/ ./app/

# Non-root user untuk keamanan
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Gunakan uvicorn dengan 2 worker agar lebih responsif di free tier
CMD ["uv", "run", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--no-access-log"]
