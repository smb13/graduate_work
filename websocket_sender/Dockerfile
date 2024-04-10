FROM python:3.11-slim as base

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN apt-get update &&  \
    apt-get install libffi-dev libpq-dev liblz4-dev libunwind-dev -y \
    && apt-get clean\
    && pip install -U pip \
    && pip install -r requirements.txt

COPY src /app/src/

FROM builder as final

RUN groupadd -r -g 1000 app_group && useradd -r -g app_group -u 1000 app_user
RUN chown -R app_user:app_group /app
USER app_user
