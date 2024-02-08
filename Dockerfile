# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.10.10
FROM python:${PYTHON_VERSION}-alpine as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
WORKDIR /app

RUN apk update && apk add ffmpeg
RUN apk add libopusenc
RUN apk add libogg
RUN apk add opus-tools
RUN python -m pip install poetry==1.7.1

COPY pyproject.toml poetry.lock ./
RUN touch README.md
RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

COPY hard_brain_bot ./hard_brain_bot
RUN poetry install --without dev --no-root

CMD ["python", "-m", "hard_brain_bot"]
