FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -U pip \
    && pip install -r requirements.txt

COPY src /app/src/

CMD uvicorn src.main:app --host ${APP_SENDER_HOST:-0.0.0.0} --port 8000
