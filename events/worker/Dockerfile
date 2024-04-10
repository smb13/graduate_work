FROM python:3.12.2

ARG ROOTDIR='/opt/app'

ENV PYTHONPATH ${ROOTDIR}

WORKDIR ${ROOTDIR}


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1


COPY requirements.txt requirements.txt

RUN pip install --upgrade pip --no-cache-dir --no-python-version-warning && \
    pip install -r requirements.txt --no-cache-dir


COPY . .

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]