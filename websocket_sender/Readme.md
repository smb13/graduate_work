# WebSocket Sender

## Отправка сообщений

Для отправки сообщений, нужно сначала отправить jwt токен для доступа к сервису

```json
{
  "jwt_token": "jwt_here"
}
```

После подключения, активизируется клиент слушателя RabbitMQ, который будет пересылать
сообщения по WebSocket пользователю

В такой структуре:

```json
{
    "request_id": "str",
    "notice_id": "UUID",
    "message_id": "UUID",
    "user_id": "UUID",
    "message_meta": {
        "key": "value"
      },
    "message_body": "str"
}
```

## Подключение клиента

Для имитации клиента можно воспользоваться кодом из файла `connect_user.py`

```bash
python ./src/utils/connect_user.py
```