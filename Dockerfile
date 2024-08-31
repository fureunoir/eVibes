# syntax=docker/dockerfile:1
FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:$PATH"

RUN sed -i 's|http://deb.debian.org/debian|http://ftp.ru.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources

RUN apt update \
    && apt install -y --no-install-recommends --fix-missing \
        build-essential \
        libpq-dev \
        gettext \
        libgettextpo-dev \
        graphviz-dev \
        libgts-dev \
        libpq5 \
        gettext \
        graphviz \
        binutils \
        libproj-dev \
        gdal-bin \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install --no-cache-dir pipx

RUN pipx install poetry

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry install --extras "graph" --extras "worker"
