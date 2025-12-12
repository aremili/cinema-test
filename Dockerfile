FROM python:3.13-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN useradd -m -u 1000 appuser

WORKDIR /app
RUN chown appuser:appuser /app

# Copy deps with user
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
USER appuser
RUN uv sync --frozen

EXPOSE 8000