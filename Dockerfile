FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    ca-certificates \
    dnsutils \
    libnss3 \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv (ultra-fast Python package manager)
RUN curl -Ls https://astral.sh/uv/install.sh | bash

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install deps (cached unless pyproject/lock changes)
RUN uv venv --python=3.11 \
    && uv pip install . 

# Then copy the rest of the app
COPY . .

# Activate virtualenv on container start
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

EXPOSE 8001

# Run your FastAPI app via start.py using uv's Python
CMD ["uv", "run", "start.py"]
