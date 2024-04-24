# Email Sender

## Использование

Документация swagger: http://127.0.0.1:9746/email-sender/api/v1/docs

Ручка для отправки письма: http://127.0.0.1:9746/email-sender/api/v1/send-email (если развернут локально)

Принимает json-структуру:

```yaml
{
  "is_priority": false,
  "retries": 0,
  "user_timezone": "Europe/Moscow",
  "message_id": "42987438-d191-4849-8e16-8535ad54d61f", 
  "message_subject": "Очень важная нотификация",
  "message_to_email": [
    "test@test.com",
    "vasya@test.com"
  ],
  "message_body": "string"
}
```

Описание:
- `is_priority` (по умолчанию `False`) = Если `True` то будет попытка отправки письма немедленно (вне зависимости от времени - по умолчанию шлем сообщения с 9 утра до 21 вечера по указанной таймзоне). Если `False` то будет отложенная отправка через сервис sendgrid
- `retries` (по умолчанию `0`) = Номер попытки (при неудачной попытке возвращается та же структура, что и пререданная, но `retries` = `retries` + 1). Сервис Нотификации сам контролирует пересылку и частоту повторов оправки. При превышении env значения `email_sender_max_retries_to_send` вернет None
- `user_timezone` (по умолчанию `Europe/Moscow`) = Можно передать указанный таймзон пользователя
- `message_id` = UUID сообщения
- `message_subject` = Тема сообщения
- `message_to_email` = Список email для рассылки
- `message_body` = Сообщение

В случае успеха вернет:

```yaml
{
  "detail": "Success"
}
```

В случае неудачной попытке вернет:

```yaml
{
  "detail": "Failure",
  "is_priority": false,
  "retries": 1, # +1 к попытке
  "user_timezone": "Europe/Moscow",
  "message_id": "42987438-d191-4849-8e16-8535ad54d61f", 
  "message_subject": "Очень важная нотификация",
  "message_to_email": [
    "test@test.com",
    "vasya@test.com"
  ],
  "message_body": "string"
}
```

При превышении кол-ва попыток вернетЖ

```yaml
{
  "detail": "The number of attempts has ended"
}
```


## Запуск проекта

Заполнить env переменные:

```text
JWT_ACCESS_TOKEN_SECRET_KEY=CHANCGE_THIS

EMAIL_SENDER_API_SENDGRID=CHANCGE_THIS
EMAIL_SENDER_FROM_EMAIL=middle-team@yandex.ru

APP_SENDER_PREFIX=email-sender
APP_SENDER_DEBUG=False
APP_SENDER_LOG_LEVEL=20
APP_SENDER_HOST=0.0.0.0
APP_SENDER_PORT=9746
```

- `JWT_ACCESS_TOKEN_SECRET_KEY` = актуальный jwt токен
- `EMAIL_SENDER_API_SENDGRID` = API ключ сервиса Sendgrid
- `EMAIL_SENDER_FROM_EMAIL` = название email с которого будет рассылка


### Локальный запуск

- `docker compose -p email-sender up -d --build --remove-orphans`