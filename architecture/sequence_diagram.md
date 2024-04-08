## Получение сведений о подписках
```mermaid
sequenceDiagram
    actor User as Пользователь
    box Subscription Service
        participant API as EPK API
        participant DB as Database
    end

    User->>API: Запрос списка подписок
    API->>DB: Запрос списка подписок
    DB->>API: Список подписок
    API->>User: Список подписок
```
## Оплата подписки
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

    User->>SubAPI: Купить подписку X за Y
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
    BillAPI->>BillDB: Статус оплаты Выполнена
    BillDB->>BillAPI: Статус оплаты сохранён
    BillAPI->>SubAPI: Идентификатор сохраненного способа оплаты
    SubAPI->>SubDB: ID способа оплаты, статус подписки
    SubDB->>SubAPI: Подписка активирована, ID сохранён
    SubAPI->>BillAPI: Данные подписки сохранены
    BillAPI->>BillDB: Статус оплаты Применена
    BillDB->>BillAPI: Статус оплаты сохранён
    
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
        participant BilAPI as Billing API
        participant BilDB as Database
    end
    participant Events as Events Service
    User->>SubAPI: Отменить подписку X
```
## Продление подписки
```mermaid
sequenceDiagram
    box Subscription Service
        participant Cron
        participant SubApp as Subscription App
        participant SubDB as Database
    end
    box Billing Service
        participant BilAPI as Billing API
        participant BilDB as Database
    end
    participant Events as Events Service
    Cron->>SubApp: Продлить подписку X
```