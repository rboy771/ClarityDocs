# Multi-stage production Dockerfile for ClarityDocs
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /uvx /bin/

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and documentation
COPY src ./src
COPY README.md ./

# Final lightweight runtime image
FROM python:3.12-slim

WORKDIR /app

# Copy virtualenv and application from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/README.md /app/README.md

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Seed the SQLite FTS5 database at container build
RUN python src/claritydocs/db/seed.py

# Expose standard port
EXPOSE 8000

# Run Uvicorn production server
CMD ["uvicorn", "claritydocs.main:app", "--host", "0.0.0.0", "--port", "8000"]
