# Проектная работа: Биллинг

## Подготовка к запуску

Все сервисы добавлены в один docker-compose файл docker-compose-dev.yml
Для запуска используется Makefile

Для запуска проекта необходимо создать файл с переменными окружения: `cp ./.env.template ./.env` и заполнить его

Сгенерировать секретный ключ можно с помощью команды `make admin_generate_secret_key`

Справка по вариантам запуска: `make help`

## Конфигурация

Билд External API основан на сборке 
[tiangolo/uvicorn-gunicorn-fastapi-docker](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker/).

Там же есть справочная информация о 
[конфигурации через переменные окружения](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker/#environment-variables).  

## Запуск для проверки работы ревьювером: Тесты

Запуск автотестов API со сборкой, распаковкой БД, загрузкой в Elastic `make first_start_tests`

Запуск автотестов повторный `make tests`

Завершение работы `make down`

## Запуск как для продакшн

Первый запуск с восстановлением БД postgres из дампа, загрузкой данных из 
Postgres в Elasticsearch и запуском проекта External API, админки и Nginx: `make first_start` или `make`

Последующие запуски проектов External API и админки с Nginx: `make start` или `make production`

Однократный запуск ETL и загрузки данных в Elasticsearch `make run_etl`

Включение отдельно службы ETL с дозагрузкой обновлений раз в минуту `make etl`

Проект запускается на `80` порту, api не запаролен

Документация на API: [localhost/api/openapi](http://localhost/api/openapi)

Админка запускается по адресу [localhost/admin/](http://localhost/admin/)

Создание суперпользователя для входа в админку на основе данных из .env: `make createsuperuser`

## Запуск для разработки

Запуск проекта External API для разработки: `make external_dev`

Проект External API запускается с функцией autoreload при изменении кода на порту `8000`

Запуск проекта Django Admin для разработки: `make admin_dev` 

Проект Django Admin запускается с функцией autoreload при изменении кода на порту `8080`

Можно запускать оба проекта для разработки одновременно

Однократный запуск ETL и загрузки данных в Elasticsearch `make run_etl`

## Для разработки в PyCharm

Для разработки рекомендуется добавить Python Interpreter On Docker Compose
на основе файла проекта /movies/docker-compose.yml

Для разработки в проекте External API используйте контейнер external_dev
Для разработки в проекте Admin используйте контейнер admin_dev
Для разработки в проекте ETL используйте контейнер etl

В образах для контейнеров *_dev дополнительно устанавливаются зависимости
для запуска автотестов pytest

## Стиль кода

Для работы над проектом строго необходимо использовать линтеры через pre-commit хуки
Установка прекоммит хуков: `pre-commit install`.
После этого PyCharm сам будет запускать их при попытке сделать коммит

Для ручного запуска линтеров и автоформаттеров: `git add . && pre-commit run` 
