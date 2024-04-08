## Администрирование видов подписок
### Запрос всех видов подписок
```mermaid
sequenceDiagram
    actor User as Администратор
    box Subscription Service
        participant API as Subscription API
        participant DB as Database
    end

    User->>API: Запрос всех видов подписок
    Note right of User: GET /api/v1/subscription-types
    API->>DB: Запрос всех видов подписок
    DB->>API: Список видов подписок
    API->>User: Список видов подписок
```
### Создание нового вида подписок
```mermaid
sequenceDiagram
    actor User as Администратор
    box Subscription Service
        participant API as Subscription API
        participant DB as Database
    end
    
    User->>API: Создание нового вида подписок
    Note right of User: POST /api/v1/subscription-types
    API->>DB: Создание нового вида подписок
    DB->>API: Новый вид подписки
    API->>User: Новый вид подписки
```
### Изменение вида подписки
```mermaid
sequenceDiagram
    actor User as Администратор
    box Subscription Service
        participant API as Subscription API
        participant DB as Database
    end
    
    User->>API: Изменение вида подписки
    Note right of User: PATCH /api/v1/subscription-types/<id>
    API->>DB: Изменение вида подписки
    DB->>API: Изменённый вид подписки
    API->>User: Изменённый вид подписки
```

## Работа с подписками пользователя
### Пользователь получает свои подписки
```mermaid
sequenceDiagram
    actor User as Пользователь
    box Subscription Service
        participant API as Subscription API
        participant DB as Database
    end

    User->>API: Пользователь запрашивает свои подписки
    Note right of User: GET /api/v1/me/user-subscriptions
    API->>DB: Пользователь запрашивает свои подписки
    DB->>API:  Список подписок пользователя
    API->>User: Список подписок пользователя
```
### Пользователь подписывается и оплачивает подписку
```mermaid
sequenceDiagram
    actor User as Покупатель
    box Subscription Service
        participant SubAPI as Subscription API
        participant SubDB as Database
    end
    box Billing Service
        participant BillBGround as Background Task
        participant BillAPI as Billing API
        participant BillDB as Database
    end
    participant YooKassa as ЮKassa
    participant Events as Events Service

    User->>SubAPI: Купить подписку X за Y
    Note right of User: POST /api/v1/me/user-subscriptions
    SubAPI->>SubDB: Проверить актуальную стоимость
    SubDB->>SubAPI: Стоимость
    SubAPI->>SubAPI: Стоимость == Y
    SubAPI->>SubDB: Проверить не подписан ли уже
    SubDB->>SubAPI: Ещё не подписан
    SubAPI->>SubDB: Создать подписку пользователя
    SubDB->>SubAPI: ID подписки

    SubAPI->>BillAPI: Сформировать Платёж за подписку X на сумму Y
    BillAPI->>YooKassa: Создать платёж и сохранить способ оплаты
    YooKassa->>YooKassa: Генерация ссылки на оплату
    YooKassa->>BillAPI: Ссылка на страницу оплаты
    BillAPI->>BillDB: Записать платёж в историю
    BillDB->>BillAPI: Новый платёж сохранён
    BillAPI->>SubAPI: Ссылка на страницу оплаты
    SubAPI->>User: Ссылка на страницу оплаты

    User->>YooKassa: Данные карты, подтверждение оплаты
    YooKassa->>YooKassa: Проведение оплаты в банке
    YooKassa->>BillAPI: Callback с результатом и сохранённым способом оплаты
    BillAPI->>BillBGround: Создать Background Task
    BillAPI->>YooKassa: Результат принят

    BillBGround->>BillDB: Статус оплаты Выполнена
    BillDB->>BillBGround: Статус оплаты сохранён
    BillBGround->>SubAPI: Идентификатор сохраненного способа оплаты
    SubAPI->>SubDB: ID способа оплаты, статус подписки
    SubDB->>SubAPI: Подписка активирована, ID сохранён
    SubAPI->>BillBGround: Данные подписки сохранены
    BillBGround->>BillDB: Статус оплаты Применена
    BillDB->>BillBGround: Статус оплаты сохранён
    BillBGround->>Events: Событие Оплата произведена
    Events->>BillBGround: Событие получено
```
## Отмена подписки
```mermaid
sequenceDiagram
    actor User as Покупатель
    box Subscription Service
        participant SubAPI as Subscription API
        participant SubDB as Database
    end
    box Billing Service
        participant BillAPI as Billing API
        participant BillDB as Database
    end
    participant YooKassa as ЮKassa
    participant Events as Events Service

    User->>SubAPI: Отменить подписку X
    Note right of User: DELETE /api/v1/me/user-subscriptions/<id>
    SubAPI->>SubDB: Получить активную подписку
    SubDB->>SubAPI: Стоимость Y, Осталось N месяцев
    alt Прошло меньше недели
        SubAPI->>BillAPI: Полный возврат
        BillAPI->>YooKassa: Создать полный возврат
        YooKassa->>BillAPI: Возврат оформлен 
        BillAPI->>BillDB: Записать возврат в историю
        BillDB->>BillAPI: Возврат сохранён
        BillAPI->>SubAPI: Возврат совершён
    else Прошло больше недели но осталось больше месяца
        SubAPI->>SubAPI: Рассчитать сумму возврата
        SubAPI->>BillAPI: Частичный возврат
        BillAPI->>YooKassa: Создать частичный возврат
        YooKassa->>BillAPI: Возврат оформлен
        BillAPI->>BillDB: Записать возврат в историю
        BillDB->>BillAPI: Возврат сохранён
        BillAPI->>SubAPI: Возврат совершён
    else Осталось меньше месяца
        SubAPI->>SubAPI: Ничего не делаем
    end
    SubAPI->>SubDB: Удаляем способ оплаты для подписки
    SubDB->>SubAPI: Способ оплаты удалён
    SubAPI->>SubDB: Устанавливаем завершение подписки
    SubDB->>SubAPI: Дата завершение подписки установлена
    SubAPI->>User: Подписка X отменена
```
## Автоматическое продление подписки
```mermaid
sequenceDiagram
    box Subscription Service
        participant Cron as Планировщик
        participant SubApp as Subscription App
        participant SubDB as Database
    end
    box Billing Service
        participant BillAPI as Billing API
        participant BillDB as Database
    end
    participant Events as Events Service
    Cron->>SubApp: Продлить подписку X
```
## Проверять истекающие подписки и предупреждать об предстоящей оплате
```mermaid
sequenceDiagram
    box Subscription Service
        participant Cron
        participant SubApp as Subscription App
        participant SubDB as Database
    end
    box Billing Service
        participant BillAPI as Billing API
        participant BillDB as Database
    end
    participant Events as Events Service
    Cron->>SubApp: Продлить подписку X
```
## Проверять истекающие подписки, формирует запрос на оплату в сервис биллинга и уведомлять о резульате
```mermaid
sequenceDiagram
    box Subscription Service
        participant Cron
        participant SubApp as Subscription App
        participant SubDB as Database
    end
    box Billing Service
        participant BillAPI as Billing API
        participant BillDB as Database
    end
    participant Events as Events Service
    Cron->>SubApp: Продлить подписку X

```
## Проверять истекшие подписки и уведомлять об неудаче и напоминать об оплате
```mermaid
sequenceDiagram
 box Subscription Service
        participant Cron
        participant SubApp as Subscription App
        participant SubDB as Database
    end
    box Billing Service
        participant BillAPI as Billing API
        participant BillDB as Database
    end
    participant Events as Events Service
    Cron->>SubApp: Продлить подписку X
```