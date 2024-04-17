# API Сервиса подписок

## Администрирование видов подписок
| Method | Endpoint                          | Description                              | Query Parameters           | Body Data                  |
|--------|-----------------------------------|------------------------------------------|----------------------------|----------------------------|
| GET    | /api/v1/subscription-types        | Администратор получает все виды подписок |                            |                            |
| POST   | /api/v1/subscription-types        | Администратор создаёт новый вид подписки |                            |                            |
| PATCH  | /api/v1/subscription-types/\<id>  | Администратор изменяет вид подписки      |                            |                            |

## Работа пользователя со своими подписками
| Method  | Endpoint                             | Description                         | Query Parameters           | Body Data                  |
|---------|--------------------------------------|-------------------------------------|----------------------------|----------------------------|
| GET     | /api/v1/me/user-subscriptions        | Пользователь получает свои подписки | user_id, subscription-type | None                       |
| POST    | /api/v1/me/user-subscriptions        | Пользователь подписывается          |                            | user_id, subscription-type |
| PATCH   | /api/v1/me/user-subscriptions/\<id>  | Пользователь отменяет подписку      |                            |                            |

## Внутренний API между сервисами
| Method | Endpoint                                  | Description                               | Query Parameters | Body Data |
|--------|-------------------------------------------|-------------------------------------------|------------------|-----------|
| POST   | /api/v1/user-subscriptions/\<id>/activate | Сервис биллинга активирует подписку       |                  |           |
| POST   | /api/v1/user-subscriptions/\<id>/cancel   | Сервис биллинга приостанавливает подписку |                  |           |
