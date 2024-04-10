FROM python:3.11
LABEL maintainer="safeflat@gmail.com"

RUN apt-get update && apt-get install -y --no-install-recommends gettext libpcre3 libpcre3-dev && apt-get clean

ARG REQUIREMENTS_DEV=False

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/src/app'
ENV DJANGO_SETTINGS_MODULE 'config.settings'

WORKDIR /src/app/

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY requirements.dev.txt /requirements.dev.txt
RUN if "$REQUIREMENTS_DEV" ; then pip install --no-cache-dir -r /requirements.dev.txt; fi

COPY . .

RUN django-admin compilemessages -l en -l ru

EXPOSE 8000

HEALTHCHECK --start-period=10s --interval=5s --timeout=2s --retries=10 \
    CMD curl -f http://localhost:8000/healthcheck/

CMD python manage.py migrate --noinput  && python manage.py collectstatic --noinput  && uwsgi --ini uwsgi.ini