FROM tiangolo/uvicorn-gunicorn:python3.11

LABEL maintainer="safeflat@gmail.com"

ENV PYTHONPATH '/src'

WORKDIR /src/

ENV VIRTUAL_ENV=/usr/local

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

COPY requirements.txt /requirements.txt
RUN /root/.cargo/bin/uv pip install --no-cache-dir -r /requirements.txt

COPY src .

EXPOSE 8000