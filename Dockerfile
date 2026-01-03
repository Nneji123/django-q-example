FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_HTTP_TIMEOUT=3000

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        unzip \
        dpkg \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY uv.lock* ./

# Lock and sync dependencies
RUN if [ -f uv.lock ]; then \
        uv sync --no-dev --locked; \
    else \
        uv lock && uv sync --no-dev; \
    fi

COPY . /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/scheduled-task-status/ || exit 1

# Default command - runs both server and cluster
CMD ["uv", "run", "python", "run.py"]

