FROM python:3.11
LABEL maintainer="safeflat@gmail.com"

RUN apt-get update && apt-get -y install cron && apt-get clean

# Add crontab file in the cron directory
COPY crontab /etc/cron.d/etl-crontab

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/etl-crontab

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/src/app'

WORKDIR /src/app/

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY . .

CMD python create_indices.py && python main.py && printenv > /etc/environment && cron && tail -f /var/log/cron.log
