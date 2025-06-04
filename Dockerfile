FROM python:3.11-slim

WORKDIR /app

# Install system dependencies

# RUN apt-get update && apt-get install -y curl build-essential ca-certificates && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    ca-certificates \
    dnsutils \
    libnss3 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy full codebase BEFORE poetry install so /src/backend exists
COPY . .

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

EXPOSE 8001

# CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
CMD ["poetry", "run", "dev"]
