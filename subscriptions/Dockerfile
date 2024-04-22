FROM tiangolo/uvicorn-gunicorn:python3.11

LABEL maintainer="smb112@yandex.ru"

ENV PYTHONPATH '/src'

WORKDIR /src/

COPY src/requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY src .

EXPOSE 8000