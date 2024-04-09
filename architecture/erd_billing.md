# ERD

```mermaid
erDiagram
    transaction["Transaction"] {
        uuid id PK "ID транзакции"
        uuid external_id "ID транзакции у партнёра"
        uuid payment_method_id "Идентификатор сохраненного способа оплаты"
        uuid refund_payment_id "Внешний ID платежа по которому возврат"
        uuid user_id "Пользователь"
        string action "Действие (payment, refund)"
        string state "Состояние (pending, succeeded, canceled)" 
        string description "Назначение платежа (Подписка X)"
        decimal amount "Сумма платежа"
        datetime dt_created "Создано"
        datetime dt_changed "Изменено"
        int attempt_cnt "Номер попытки"
        int attempt_date "Дата последней попытки"
    }
```

Поле payment_method_id по сути идентифицирует автоплатёж по конкретной подписке

Поле refund_payment_id заполняется только для Транзакций action == refund и в нём
указывается внешний ID того платежа, по которому сделан возврат

При этом, поле payment_method_id также заполняется, если отменяемый платёж
был периодическим (с автопродлением)
