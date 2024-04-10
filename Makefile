#!make
.PHONY: admin auth etl db_dump tests external websocket_sender

include ./.env

DOCKER_COMPOSE_PROD = --env-file ./.env -f ./docker-compose.yml
DOCKER_COMPOSE_DEV = --env-file ./.env -f ./docker-compose-dev.yml
DOCKER_COMPOSE_TESTS = --env-file ./.env -f ./docker-compose-dev.yml -f ./docker-compose-tests.yml

# Default, Help

default: first_start_dev

help: # Вывод информации make командах
	@grep -E '^[a-zA-Z0-9 _-]+:.*#' Makefile | while read -r l; \
	do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# Start, First start

first_start: postgres db_create admin_migrate redis redis_auth elastic etl prod auth_migrations auth_createsuperuser

first_start_dev: postgres_dev db_create db_restore redis_dev redis_auth_dev flush_redis_dev elastic_dev clear_elastic_index_dev etl_dev dev auth_createsuperuser_dev

start: prod auth_migrations

# Tests

first_start_tests: postgres_dev db_create db_restore redis_dev redis_auth_dev flush_redis_dev elastic_dev clear_elastic_index_dev etl_dev tests

tests:
	docker compose $(DOCKER_COMPOSE_TESTS) up --build --attach tests

# Profiles

prod:
	docker compose $(DOCKER_COMPOSE_PROD) up -d

dev:
	docker compose $(DOCKER_COMPOSE_DEV) up -d --build --remove-orphans

# Redis

redis:  # Запустить контейнер Redis server
	docker compose $(DOCKER_COMPOSE_PROD) up --wait -d redis

redis_dev:  # Запустить контейнер Redis server
	docker compose $(DOCKER_COMPOSE_DEV) up --wait -d redis

redis_auth:  # Запустить контейнер Redis server Auth
	docker compose $(DOCKER_COMPOSE_PROD) up --wait -d redis_auth

redis_auth_dev:  # Запустить контейнер Redis server Auth
	docker compose $(DOCKER_COMPOSE_DEV) up --wait -d redis_auth

flush_redis_dev:  # Очистить хранилище Redis State
	docker compose $(DOCKER_COMPOSE_DEV) run redis redis-cli -h redis -c "FLUSHALL"

clear_redis_state_dev:  # Очистить хранилище Redis State
	docker compose $(DOCKER_COMPOSE_DEV) run redis redis-cli -h redis -c "DEL" "state_data"

# Elasticsearch

elastic:  # Собрать и запустить контейнер ElasticSearch и должаться статуса healthy
	docker compose $(DOCKER_COMPOSE_PROD) up --build -d elastic --wait

elastic_dev:  # Собрать и запустить контейнер ElasticSearch и должаться статуса healthy
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d elastic --wait

etl:  # Собрать и запустить контейнер приложения ETL из Postgres в ElasticSearch
	docker compose $(DOCKER_COMPOSE_PROD) up --build -d etl

etl_dev:  # Собрать и запустить контейнер приложения ETL из Postgres в ElasticSearch
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d etl

clear_elastic_index_dev:  # Очистить индекс Elasticsearch
	docker compose $(DOCKER_COMPOSE_DEV) run elastic curl -XDELETE http://elastic:9200/movies \
	&& docker compose $(DOCKER_COMPOSE_DEV) run elastic curl -XDELETE http://elastic:9200/persons \
	&& docker compose $(DOCKER_COMPOSE_DEV) run elastic curl -XDELETE http://elastic:9200/genres

# PostgreSQL

postgres:  # Собрать и запустить контейнер Postgres
	docker compose $(DOCKER_COMPOSE_PROD) up --build --force-recreate -d postgres

postgres_dev:  # Собрать и запустить контейнер Postgres
	docker compose $(DOCKER_COMPOSE_DEV) up --build --force-recreate -d postgres

db_dump: # Сделать дамп базы данных Postgres в файл ./db_dump/movies_db.backup
	docker compose $(DOCKER_COMPOSE_DEV) exec -i postgres bash -c "pg_dump -U $(POSTGRES_USER) "\
	"-Fc -f /etc/db_dump/movies_db.backup $(POSTGRES_MOVIES_DB)"

db_create: db_create_movies db_create_auth db_create_scheduler # Создать базы данных для сервисов

db_create_movies: # Создать базу данных для сервиса movies
	docker compose $(DOCKER_COMPOSE_PROD) exec -i postgres bash -c "/etc/db_dump/wait-for-postgres.sh localhost && "\
	"echo \"SELECT 'CREATE DATABASE $(POSTGRES_MOVIES_DB)' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = "\
	"'$(POSTGRES_MOVIES_DB)')\gexec\" | psql -U $(POSTGRES_USER)"

db_create_auth: # Создать базу данных для сервиса auth
	docker compose $(DOCKER_COMPOSE_PROD) exec -i postgres bash -c "/etc/db_dump/wait-for-postgres.sh localhost && "\
	"echo \"SELECT 'CREATE DATABASE $(POSTGRES_AUTH_DB)' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = "\
	"'$(POSTGRES_AUTH_DB)')\gexec\" | psql -U $(POSTGRES_USER)"

db_create_scheduler: # Создать базу данных для сервиса scheduler
	docker compose $(DOCKER_COMPOSE_PROD) exec -i postgres bash -c "/etc/db_dump/wait-for-postgres.sh localhost && "\
	"echo \"SELECT 'CREATE DATABASE $(POSTGRES_SCHEDULER_DB)' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = "\
	"'$(POSTGRES_SCHEDULER_DB)')\gexec\" | psql -U $(POSTGRES_USER)"

db_drop_auth: # Удалить базу данных для сервиса auth
	docker compose $(DOCKER_COMPOSE_PROD) exec -i postgres bash -c "/etc/db_dump/wait-for-postgres.sh localhost && "\
	"echo \"SELECT 'DROP DATABASE $(POSTGRES_AUTH_DB)' WHERE EXISTS (SELECT FROM pg_database WHERE datname = "\
	"'$(POSTGRES_AUTH_DB)')\gexec\" | psql -U $(POSTGRES_USER)"

db_restore: # Восстановить базу данных Postgres из файла ./db_dump/movies_db.backup
	docker compose $(DOCKER_COMPOSE_DEV) exec -i postgres bash -c "/etc/db_dump/wait-for-postgres.sh localhost && "\
	"pg_restore -U $(POSTGRES_USER) -Fc -c --if-exists -O -v --no-acl -d $(POSTGRES_MOVIES_DB) /etc/db_dump/movies_db.backup"

# External API

external:  # Собрать и запустить контейнер External API
	docker compose $(DOCKER_COMPOSE_PROD) up --build -d external

external_dev:  # Собрать и запустить тестовый контейнер External API (с зависимостями для разработки)
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d external_dev

# Notification Service

notification_dev:
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d

notification_stop:
	docker compose $(DOCKER_COMPOSE_DEV) stop

# Auth

auth:  # Собрать и запустить тестовый контейнер Auth (с зависимостями для разработки)
	docker compose $(DOCKER_COMPOSE_PROD) up --build -d auth

auth_dev:  # Собрать и запустить тестовый контейнер Auth (с зависимостями для разработки)
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d auth_dev

auth_createsuperuser:  # Создать суперпользователя по параметрам LOCAL_USER_EMAIL LOCAL_USER_PASSWORD из .env
	@docker compose $(DOCKER_COMPOSE_PROD) run --rm auth bash -c \
    'python /src/commands/create_admin.py --username $(LOCAL_USER_EMAIL) --password $(LOCAL_USER_PASSWORD)'

auth_createsuperuser_dev:  # Создать суперпользователя по параметрам LOCAL_USER_EMAIL LOCAL_USER_PASSWORD из .env
	@docker compose $(DOCKER_COMPOSE_DEV) run --rm auth_dev bash -c \
    'python /src/commands/create_admin.py --username $(LOCAL_USER_EMAIL) --password $(LOCAL_USER_PASSWORD)'

## make auth_upgrade_migration: команда для создания новой ревизии
auth_upgrade_migration:
	docker compose $(DOCKER_COMPOSE_PROD) run --rm --no-deps auth alembic revision --autogenerate -m "${MESSAGE}"

## make auth_migrations: команда для запуска всех миграций бд
auth_migrations:
	docker compose $(DOCKER_COMPOSE_PROD) run --rm auth alembic upgrade head

## make auth_downgrade_migration: команда для отката последней ревизии
auth_downgrade_migration:
	docker compose $(DOCKER_COMPOSE_PROD) run --rm auth alembic downgrade -1


# Django Admin

admin:  # Собрать и запустить контейнер Django Admin
	docker compose $(DOCKER_COMPOSE_PROD) up --build -d admin

admin_dev:  # Собрать и запустить тестовый контейнер Django Admin (с зависимостями для разработки и запуска автотестов)
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d admin_dev

admin_migrate:  # Запустить миграции Django для создания структуры базы данных
	@docker compose $(DOCKER_COMPOSE_PROD) run --rm admin bash -c "python ./manage.py migrate"

admin_createsuperuser_dev:  # Создать суперпользователя по параметрам LOCAL_USER LOCAL_USER_EMAIL LOCAL_USER_PASSWORD из .env
	@docker compose $(DOCKER_COMPOSE_DEV) run --rm admin_dev bash -c 'echo "from django.contrib.auth import get_user_model;'\
	'User = get_user_model(); User.objects.create_superuser(\"$(LOCAL_USER)\", \"$(LOCAL_USER_EMAIL)\", '\
	'\"$(LOCAL_USER_PASSWORD)\") if not User.objects.filter(username=\"$(LOCAL_USER)\").exists() '\
	'else print(\"Имя суперпользователя занято\")" | python manage.py shell'

admin_generate_secret_key:
	@docker compose $(DOCKER_COMPOSE_PROD) run --rm admin bash -c \
	'python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'

admin_generate_secret_key_dev:
	@docker compose $(DOCKER_COMPOSE_DEV) run --rm admin_dev bash -c \
	'python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'


# Scheduler

scheduler:  # Собрать и запустить контейнер Events Scheduler
	docker compose $(DOCKER_COMPOSE_PROD) up --build -d scheduler

scheduler_dev:  scheduler_dev_web scheduler_beat # Собрать и запустить контейнеры Events Scheduler в режиме отладки

scheduler_dev_web:  # Собрать и запустить контейнер Events Scheduler в режиме отладки
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d scheduler

scheduler_beat:  # Собрать и запустить контейнер Events Scheduler Celery Beat в режиме отладки
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d scheduler_beat

scheduler_migrate:  # Запустить миграции Django Events Scheduler для создания структуры базы данных
	@docker compose $(DOCKER_COMPOSE_PROD) run --rm scheduler bash -c "python ./manage.py migrate"

scheduler_createsuperuser_dev:  # Создать суперпользователя Events Scheduler по параметрам из .env
	@docker compose $(DOCKER_COMPOSE_DEV) run --rm scheduler bash -c 'echo "from django.contrib.auth import get_user_model;'\
	'User = get_user_model(); User.objects.create_superuser(\"username:$(LOCAL_USER_EMAIL)\", \"$(LOCAL_USER_EMAIL)\", '\
	'\"$(LOCAL_USER_PASSWORD)\") if not User.objects.filter(username=\"username:$(LOCAL_USER_EMAIL)\").exists() '\
	'else print(\"Имя суперпользователя занято\")" | python manage.py shell'

# Mongo DB

mongo_dev: # Запуск всех контейнеров
	docker compose $(DOCKER_COMPOSE_DEV) up -d mongocfg1 mongors1n1 mongos1

mongo_dev_first_start: mongo_dev mongo_config mongo_config_shards mongo_config_routers_shards # Первый запуск

mongo_config: # Конфигурация серверов конфигурации
	docker compose $(DOCKER_COMPOSE_DEV) exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}]})" | mongosh'

mongo_config_shards: # Конфигурация шардов
	docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}]})" | mongosh'

mongo_config_routers_shards: # Конфигурация роутеров
	docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh'

mongo_logs: # Журнал
	docker compose $(DOCKER_COMPOSE_DEV) logs --tail 100 -f

# Events EPK Services

epk_dev: epk_api_dev epk_workers_dev # Запустить сервисы EPK

epk_api_dev:
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d epk_api

epk_workers_dev:
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d worker_email_general_notice worker_email_weekly_bookmarks worker_push_general_notice worker_push_review_like

# Websocket sender

websocket_sender: #
	docker compose $(DOCKER_COMPOSE_DEV) up --build -d websocket-sender

# Rabbit MQ

rabbit: # Запустить брокер RabbitMQ
	docker compose $(DOCKER_COMPOSE_DEV) up -d rabbit

# Filebeat

filebeat_dev: # Отобразить логи заданного приложения
	docker compose $(DOCKER_COMPOSE_DEV) up -d filebeat

elasticsearch_logs_dev: # Отобразить логи elasticsearch-logs
	docker compose $(DOCKER_COMPOSE_DEV) logs -f --tail=200 elasticsearch-logs

# Stop & Down

stop:
	docker compose $(DOCKER_COMPOSE_PROD) stop

stop_dev:
	docker compose $(DOCKER_COMPOSE_DEV) stop

down:
	docker compose $(DOCKER_COMPOSE_PROD) down --remove-orphans

down_full:
	docker compose $(DOCKER_COMPOSE_PROD) down -v --rmi all --remove-orphans

clear: ## Команда для очистки всех контейнеров и образов (удалит вообще всё)
	docker system prune -a
	docker volume prune

# Misc

chown_migrations:
	sudo find . -type f -path '*/migrations/*.py' -exec chown ${USER}:${USER} {} +
