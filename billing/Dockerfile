FROM tiangolo/uvicorn-gunicorn:python3.11

LABEL maintainer="safeflat@gmail.com"

ENV PYTHONPATH '/src'

WORKDIR /src/

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY src .

EXPOSE 8000