FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
COPY pyproject.toml poetry.lock ./
RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-root --without dev

COPY . .