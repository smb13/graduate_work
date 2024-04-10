# ELK сервис


## Подключение сервисов к ELK

### Использование Gelf

Добавить в docker compose чтобы приложение отправляло логи

```yaml
    logging:
      driver: gelf
      options:
        gelf-address: udp://127.0.0.1:5044
        tag: nginx
```

Изменить:
- `tag` имя своего сервиса
- `127.0.0.1:5044` IP взять из VM яндекса с сервиса ELK, порт оставить

### Использование Filebeat (логов в файлах)

Для этого нужно добавить 

```yaml
  filebeat-service-api:
    image: elastic/filebeat:8.12.0
    build:
      context: ./deploy/filebeat
    volumes:
      - filebeat_logs:/var/log/filebeat
    depends_on:
      - kibana-logs
      - elasticsearch-logs
      - logstash
...
volumes:
  filebeat_logs:
```

В настройке сервиса в докере не забудьте так же добавить volume к сервису для хранения логов

```yml
...
# Данный volume также прописать в приложении где планируется собирать логи в файле
# /opt/log - путь куда складывать логи в самом приложении
    volumes:
      - filebeat_logs:/opt/log
...
```

И задать настройки в файле `filebeat.yml`

```yml
name: "apps-service-filebeat"
logging.metrics.enabled: false
xpack.security.enabled: false
xpack.monitoring.enabled: false
setup.ilm.enabled: false
setup.template.enabled: false

filebeat.inputs:
  - type: filestream
    scan_frequency: 1s
    enabled: true
    paths:
      - /var/log/filebeat/*
    tags: [ "apps" ]
    json:
      keys_under_root: true
      add_error_key: true

    processors:
      - decode_json_fields:
          fields: [ "message" ]
          process_array: false
          max_depth: 2
          target: ""
          overwrite_keys: true
          add_error_key: false

output.logstash:
  enabled: true
  hosts: [ "logstash:5044" ]
```

В поле `tags` укажите нужный тег для приложения

> Подробности про особенность фильтрации полей с тегами ниже



### Настройка сервисов под единый формат логов

> Для включения режима фильтрации логов - в поле tag (при настройке gelf) укажите `apps` или `nginx` (только для самого nginx)

Формат логов:

- `'%(asctime)s [%(levelname)s] [in %(filename)s: line %(lineno)d] - "%(message)s"'` - такого формата логов нужно придерживаться для сервисов
- `datefmt="[%Y-%m-%d %H:%M:%S %z]"` - формат даты и времени

Пример установки настроек для логгера

```python
import logging

log_format: str = '%(asctime)s [%(levelname)s] [in %(filename)s: line %(lineno)d] - "%(message)s"'
logging.basicConfig(format=log_format, level=10, datefmt="[%Y-%m-%d %H:%M:%S %z]")
```

### Настройка сервиса без фильтрации

Для этого достаточно задать любой другой `tag` (при настройке gelf) для приложения


## Запуск ELK

Перед запуском не забудьте настроить `.env` -> можно взять готовый вариант из `.env-example`

```bash
cp ./.env-example ./.env
```

## Kibana

Сервис будет доступен по адресу (если не менять порты): http://127.0.0.1:5601  (либо по своему настроенному IP адресу)

### Настройка веб-интерфейса

Для отображения логов в Kibana требуется завести Index Pattern.

Он может полностью совпадать с названием индекса, а может включать в себя несколько индексов с похожими названиями.

Например, если ваши логи пишутся в разные индексы в зависимости от даты: logs-2020.12.31, logs-2022.01.01, logs-2023.01.02, то Index Pattern logs* агрегирует записи из всех индексов с префиксом logs, а паттерн logs-2023* будет показывать только результаты за 2023 год.

Чтобы завести паттерн, перейдите в Management → Stack Management → Data Views и нажмите Create data view.

Если ES уже получил какие-то данные, то в списке вы увидите названия индексов, в которых они хранятся.

На следующем шаге вам предложат выбрать поле, на котором будет базироваться поиск логов по времени. Возможно, вы заметили, что logstash добавил к вашему сообщению timestamp. Выбирайте его.

После создания паттерна перейдите в Kibana → Discover, чтобы посмотреть содержимое индексов.

В левой части отображаются все распознанные в сообщения поля.

Справа — график и список сообщений.

Вверху находится поисковая строка, принимающая KQl-запросы. Их синтаксис весьма прост, вы можете убедиться в этом в официальной документации.

### Пример KQl запроса

Запрос который покажет все логи в котором в поле `message` содержится слово `число`:

```text
message : число
```

