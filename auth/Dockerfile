FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

LABEL maintainer="safeflat@gmail.com"

ARG REQUIREMENTS_DEV=False

ENV PYTHONPATH '/src'

WORKDIR /src/

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY requirements.dev.txt /requirements.dev.txt
RUN if "$REQUIREMENTS_DEV" ; then pip install --no-cache-dir -r /requirements.dev.txt ; fi

COPY src .
COPY migration ./migration
COPY alembic.ini .

EXPOSE 8000