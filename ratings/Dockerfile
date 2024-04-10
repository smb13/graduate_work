FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ARG REQUIREMENTS_DEV=False

ENV PYTHONPATH '/src'

WORKDIR /src/

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY src .

EXPOSE 8000
