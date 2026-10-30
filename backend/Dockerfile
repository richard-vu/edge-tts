FROM python:3.14-slim

# Copy uv binary from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for Python and uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first for optimal Docker layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code and Alembic migrations
COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src

# Create data directory with sticky bit permission (1755)
RUN mkdir -p /app/data && chmod 1755 /app/data

EXPOSE 8000

# Run database migrations via Alembic and start the FastAPI server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000"]

