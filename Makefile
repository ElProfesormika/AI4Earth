.PHONY: up down logs backend-shell db-shell migrate seed simulate train test smoke install-compose

COMPOSE := $(shell bash scripts/compose.sh)

ifeq ($(COMPOSE),)
$(warning Docker Compose not found. Run: make install-compose)
endif

up:
	@test -n "$(COMPOSE)" || (echo "ERROR: install Docker Compose first → make install-compose" && exit 1)
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f

backend-shell:
	$(COMPOSE) exec backend bash

db-shell:
	$(COMPOSE) exec db psql -U smartwaste smartwaste

migrate:
	$(COMPOSE) exec backend alembic upgrade head

seed:
	$(COMPOSE) exec -e PYTHONPATH=/app backend python /app/scripts/seed_demo_data.py

simulate:
	$(COMPOSE) up simulator --build

train:
	$(COMPOSE) run --rm ml python -m src.training.train_yolo

test:
	$(COMPOSE) exec backend pytest -v

smoke:
	bash scripts/smoke_test.sh

install-compose:
	@echo "Installing docker-compose-v2 (Ubuntu)..."
	sudo apt update && sudo apt install -y docker-compose-v2
	@echo "Done. Verify with: docker-compose version"
