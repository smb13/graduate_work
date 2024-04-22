# API Сервиса подписок

## Типы подписок
| Method | Endpoint                         | Description                                                        | Query Parameters | Body Data    |
|--------|----------------------------------|--------------------------------------------------------------------|------------------|--------------|
| GET    | /api/v1/subscription-types       | Администратор или пользователь получает все типы подписок          |                  |              |
| POST   | /api/v1/subscription-types       | Администратор создаёт новый тип подписки                           |                  |              |
| PATCH  | /api/v1/subscription-types/\<id> | Администратор изменяет тип подписки                                |                  |              |
| GET    | /api/v1/subscription-types/\<id> | Администратор или пользователь получает тип подписки по id         |                  |              |
| GET    | /api/v1/user-subscription-types  | Администратор или пользователь получает все типы активных подписок |                  |              |

## Работа пользователя со своими подписками
| Method  | Endpoint                             | Description                         | Query Parameters           | Body Data                  |
|---------|--------------------------------------|-------------------------------------|----------------------------|----------------------------|
| GET     | /api/v1/me/user-subscriptions        | Пользователь получает свои подписки | user_id, subscription-type | None                       |
| POST    | /api/v1/me/user-subscriptions        | Пользователь подписывается          |                            | user_id, subscription-type |
| PATCH   | /api/v1/me/user-subscriptions/\<id>  | Пользователь отменяет подписку      |                            |                            |

## Внутренний API между сервисами
| Method | Endpoint                                  | Description                               | Query Parameters           | Body Data |
|--------|-------------------------------------------|-------------------------------------------|----------------------------|-----------|
| POST   | /api/v1/user-subscriptions/\<id>/activate | Сервис биллинга активирует подписку       |                            |           |
| POST   | /api/v1/user-subscriptions/\<id>/cancel   | Сервис биллинга приостанавливает подписку |                            |           |
| GET    | /api/v1/user-subscriptions/               | Получить подписки пользователя            | user_id, subscription-type |           |
