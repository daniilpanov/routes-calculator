ARGS = $(filter-out $@,$(MAKECMDGOALS))

.PHONY: build prod dev test lint lint-frontend lint-backend update export-deps alembic migrate

build:
	docker buildx bake $(ARGS)

prod:
	@trap 'docker compose down' EXIT; docker compose up $(ARGS)

dev:
	@trap './scripts/stop-dev.sh' EXIT; ./scripts/run-dev.sh $(ARGS)

test:
	./scripts/run-test.sh $(ARGS)

lint:
	pre-commit run --all-files $(ARGS)
	cd Node/apps/user-frontend && npm run lint && npm run build
	cd Node/apps/admin-frontend && npm run lint

lint-frontend:
	cd Node/apps/user-frontend && npm run lint && npm run build
	cd Node/apps/admin-frontend && npm run lint

lint-backend:
	pre-commit run --all-files $(ARGS)

update:
	./scripts/prod-update.sh $(ARGS)

export-deps:
	./scripts/export-python-dependencies.sh $(ARGS)

alembic:
	./scripts/alembic-proxy.sh $(ARGS)

migrate:
	./scripts/prod-db-migrate.sh $(ARGS)

%:
	@true
