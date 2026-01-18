FROM python:3.11-slim AS python-base
LABEL authors="pedrotreccani"
ARG PORT=8085:8085

WORKDIR /code

FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY ./pyproject.toml ./uv.lock /code/
RUN uv sync --project /code/

COPY ./src/ /code/src/

EXPOSE ${PORT}

WORKDIR /code/src/app

ENTRYPOINT uv run python -m uvicorn api:router --reload --host 0.0.0.0 --port 8085
