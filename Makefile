# Constants
SRC=princesse_bd_backend
API_NAME=princesse_bd_backend_db_1

# Commands
compose_cmd = docker-compose -f ./docker-compose.yml --env-file=environment
down_cmd = $(compose_cmd) down --remove-orphans
exec_cmd = docker exec -it $(API_NAME)
attach_cmd = docker attach $(API_NAME)

down:
	@echo "Removing containers and orphans..."
	@$(down_cmd)

down_all:
	@echo "Removing containers with their volumes and images..."
	@$(down_cmd) --volumes

exec:
	@$(exec_cmd) bash

pdb:
	@$(attach_cmd)

logs:
	@$(compose_cmd) logs --tail=all -f | grep $(API_NAME)

start:
	@$(compose_cmd) start

test:
	docker exec -w /code/$(SRC) $(API_NAME) pytest --ds=settings.test

shell:
	docker exec -it -w /code/$(SRC) $(API_NAME) python manage.py shell_plus

up:
	@$(compose_cmd) up -d

build:
	@$(compose_cmd) build

celery:
	docker exec -w /code/$(SRC) $(API_NAME) ./celeryd.sh