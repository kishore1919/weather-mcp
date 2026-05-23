# Stage 1: Builder
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and install project
COPY src ./src
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment and project from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY pyproject.toml ./

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Environment variables
ENV OPENWEATHER_API_KEY=""
ENV OPENROUTER_API_KEY=""

# Expose the default FastMCP port and Gradio port
EXPOSE 8000
EXPOSE 7860

# Default to running the server
CMD ["weather-mcp"]
