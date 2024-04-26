# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y build-essential curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install and configure Poetry
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_PATH="/venv"
ENV POETRY_VIRTUALENVS_IN_PROJECT=0
ENV POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-cache --no-root

# Generate Prisma client
COPY schema.prisma /app/
RUN poetry run prisma generate

# Copy project code
COPY project/ /app/project/

# Serve the application on port 8000
CMD poetry run uvicorn project.server:app --host 0.0.0.0 --port 8000
EXPOSE 8000
