
dev:
	@docker compose -f docker-compose.yml up --build

run:
	@docker compose -f docker-compose.yml up --build -d

down:
	@docker compose -f ./docker-compose.yml down --remove-orphans

shell:
	@docker exec -it tracey_api bash

tests:
	@docker exec -it tracey_api poetry run pytest

coverage:
	@docker exec -it tracey_api poetry run coverage run -m pytest
	@docker exec -it tracey_api poetry run coverage report

mypy:
	@docker exec -it tracey_api poetry run mypy .

.PHONY: dev run down shell tests coverage mypy
