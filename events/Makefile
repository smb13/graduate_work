#!make
.PHONY: api core db models schemas services

include ./configs/.env

DOCKER_COMPOSE_EPK = --env-file ./.env -f ./docker-compose.yml
DOCKER_COMPOSE_DEV = --env-file ./.env -f ./docker-compose-dev.yml

# Default, Help

default: epk_up

help: # Вывод информации make командах
	@grep -E '^[a-zA-Z0-9 _-]+:.*#' Makefile | while read -r l; \
	do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

# Start, First start

epk_up:
	docker compose $(DOCKER_COMPOSE_EPK) up -d

dev_up:
	docker compose $(DOCKER_COMPOSE_DEV) up -d

# Build

epk_build:
	docker compose $(DOCKER_COMPOSE_EPK) build

dev_build:
	docker compose $(DOCKER_COMPOSE_DEV) build

# Logs

epk_api_logs:
	docker compose $(DOCKER_COMPOSE_EPK) logs --tail 100 -f epk_api

workers_logs:
	docker compose $(DOCKER_COMPOSE_EPK) logs --tail 100 -f  | grep "worker*"

rabbitmq_logs:
	docker compose $(DOCKER_COMPOSE_EPK) logs --tail 100 -f rabbitmq

dev_epk_api_logs:
	docker compose $(DOCKER_COMPOSE_DEV) logs --tail 100 -f epk_api

dev_workers_logs:
	docker compose $(DOCKER_COMPOSE_DEV) logs --tail 100 -f  | grep "worker*"

dev_rabbitmq_logs:
	docker compose $(DOCKER_COMPOSE_DEV) logs --tail 100 -f kafka

# Stop & Down

dev_stop:
	docker compose $(DOCKER_COMPOSE_DEV) stop

epk_stop:
	docker compose $(DOCKER_COMPOSE_EPK) stop

dev_stop:
	docker compose $(DOCKER_COMPOSE_DEV) stop

epk_down:
	docker compose $(DOCKER_COMPOSE_EPK) down --remove-orphans

dev_down:
	docker compose $(DOCKER_COMPOSE_DEV) down --remove-orphans
