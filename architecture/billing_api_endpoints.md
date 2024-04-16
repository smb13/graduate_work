# API Сервиса биллинга

## Работа пользователя со своими платежами
| Method | Endpoint              | Description               | Query Parameters | Body Data |
|--------|-----------------------|---------------------------|------------------|-----------|
| GET    | /api/v1/me/payments   | Получить историю платежей |                  |           |

## Внутренний API, с которым работает сервис подписок
| Method | Endpoint                | Description     | Query Parameters | Body Data         |
|--------|-------------------------|-----------------|------------------|-------------------|
| POST   | /api/v1/payments/new    | Создать оплату  |                  |                   |
| POST   | /api/v1/payments/renew  | Продлить оплату |                  | payment_method_id |
| POST   | /api/v1/payments/refund | Создать возврат |                  | payment_method_id |
