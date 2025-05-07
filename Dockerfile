# syntax=docker/dockerfile:1
FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN set -eux; \
    sed -i 's|https://deb.debian.org/debian|https://ftp.uk.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources; \
    apt update; \
    apt install -y --no-install-recommends --fix-missing \
        build-essential \
        libpq-dev \
        gettext \
        libgettextpo-dev \
        graphviz-dev \
        libgts-dev \
        libpq5 \
        graphviz \
        binutils \
        libproj-dev \
        postgresql-client \
        gdal-bin; \
    rm -rf /var/lib/apt/lists/*; \
    pip install --upgrade pip; \
    curl -sSL https://install.python-poetry.org | python3

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry install -E graph -E worker -E AI -E sentry

COPY . .