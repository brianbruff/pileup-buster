FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Copy source code
COPY . .

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Install Playwright browsers using Poetry's Python environment
# This ensures we use the same Python that Poetry is managing
RUN poetry run playwright install chromium \
    && poetry run playwright install-deps chromium

# Expose port
EXPOSE 8000

# Default command (can be overridden by docker-compose)
CMD ["poetry", "run", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
