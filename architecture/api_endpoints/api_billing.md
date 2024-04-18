# API Сервиса биллинга

## Работа пользователя со своими платежами
| Method | Endpoint              | Description               | Query Parameters | Body Data |
|--------|-----------------------|---------------------------|------------------|-----------|
| GET    | /api/v1/me/payments   | Получить историю платежей |                  |           |

## Внутренний API, с которым работает сервис подписок
| Method | Endpoint                | Description     | Query Parameters | Body Data                                                 |
|--------|-------------------------|-----------------|------------------|-----------------------------------------------------------|
| POST   | /api/v1/payments/new    | Создать оплату  |                  | user_id, description, amount, currency                    |
| POST   | /api/v1/payments/renew  | Продлить оплату |                  | user_id, description, amount, currency, payment_method_id |
| POST   | /api/v1/payments/refund | Создать возврат |                  | user_id, description, amount, currency, payment_method_id |
