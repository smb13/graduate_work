FROM elastic/filebeat:8.12.0

ADD ./filebeat.yml /usr/share/filebeat/filebeat.yml

USER root

RUN chown -R root /usr/share/filebeat/
RUN chmod -R go-w /usr/share/filebeat/
