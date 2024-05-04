# syntax=docker/dockerfile:1

FROM python:3.10.13-alpine as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
    
WORKDIR /app

RUN apk update && apk add \
    ffmpeg \
    libopusenc \
    libogg \
    opus-tools && \
    python -m pip install wheel poetry==1.7.1

COPY pyproject.toml poetry.lock ./
RUN touch README.md && \
    poetry install --without dev && rm -rf $POETRY_CACHE_DIR

COPY hard_brain_bot ./hard_brain_bot
RUN poetry install --without dev --no-root

CMD ["python", "-m", "hard_brain_bot"]
