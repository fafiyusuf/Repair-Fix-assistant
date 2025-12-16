.PHONY: help build run stop clean logs shell test dev prod

# Variables
IMAGE_NAME = ifix-ai-backend
CONTAINER_NAME = ifix-ai-backend
DEV_CONTAINER_NAME = ifix-ai-backend-dev
PORT = 8000

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image
	docker build -t $(IMAGE_NAME):latest .

build-prod: ## Build production Docker image
	docker build --target production -t $(IMAGE_NAME):prod .

build-dev: ## Build development Docker image
	docker build --target development -t $(IMAGE_NAME):dev .

run: ## Run the container in production mode
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):8000 \
		--env-file .env \
		$(IMAGE_NAME):latest

dev: ## Run the container in development mode with hot reload
	docker run -d \
		--name $(DEV_CONTAINER_NAME) \
		-p $(PORT):8000 \
		--env-file .env \
		-v $(PWD)/app:/app/app \
		$(IMAGE_NAME):dev

compose-up: ## Start services using docker-compose
	docker-compose up -d

compose-dev: ## Start development services using docker-compose
	docker-compose up backend-dev

compose-down: ## Stop services using docker-compose
	docker-compose down

stop: ## Stop the running container
	docker stop $(CONTAINER_NAME) || true
	docker stop $(DEV_CONTAINER_NAME) || true

clean: stop ## Stop and remove containers, images
	docker rm $(CONTAINER_NAME) || true
	docker rm $(DEV_CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME):latest || true
	docker rmi $(IMAGE_NAME):prod || true
	docker rmi $(IMAGE_NAME):dev || true

logs: ## View container logs
	docker logs -f $(CONTAINER_NAME)

logs-dev: ## View development container logs
	docker logs -f $(DEV_CONTAINER_NAME)

shell: ## Open a shell in the running container
	docker exec -it $(CONTAINER_NAME) /bin/bash

shell-dev: ## Open a shell in the development container
	docker exec -it $(DEV_CONTAINER_NAME) /bin/bash

health: ## Check container health
	@curl -f http://localhost:$(PORT)/health || echo "Service is not healthy"

ps: ## Show running containers
	docker ps -a | grep $(IMAGE_NAME)

stats: ## Show container stats
	docker stats $(CONTAINER_NAME)

prune: ## Remove all unused Docker resources
	docker system prune -af

rebuild: clean build run ## Clean, rebuild, and run

test: ## Run tests in container
	docker run --rm \
		--env-file .env \
		$(IMAGE_NAME):latest \
		pytest -v

format: ## Format code using black
	docker run --rm \
		-v $(PWD):/app \
		$(IMAGE_NAME):dev \
		black app/

lint: ## Lint code using flake8
	docker run --rm \
		-v $(PWD):/app \
		$(IMAGE_NAME):dev \
		flake8 app/

push: ## Push image to registry (set REGISTRY variable)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Error: REGISTRY variable not set. Usage: make push REGISTRY=your-registry/repo"; \
		exit 1; \
	fi
	docker tag $(IMAGE_NAME):latest $(REGISTRY):latest
	docker push $(REGISTRY):latest
