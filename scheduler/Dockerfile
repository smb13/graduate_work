FROM python:3.11
LABEL maintainer="safeflat@gmail.com"

RUN apt-get update && apt-get install -y --no-install-recommends gettext libpcre3 libpcre3-dev && apt-get clean

ARG REQUIREMENTS_DEV=False
ARG COMPILE_MESSAGES=False

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/src'
ENV DJANGO_SETTINGS_MODULE 'config.settings'

WORKDIR /src

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY requirements.dev.txt /requirements.dev.txt
RUN if "$REQUIREMENTS_DEV" ; then pip install --no-cache-dir -r /requirements.dev.txt; fi

COPY . .

RUN if "$COMPILE_MESSAGES" ; then django-admin compilemessages -l en -l ru; fi

EXPOSE 8000

CMD python manage.py migrate --noinput  && python manage.py collectstatic --noinput  && uwsgi --ini uwsgi.ini