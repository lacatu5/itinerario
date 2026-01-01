.PHONY: help test clean install lint build deploy

help:
	@echo "test            - Run tests for all services"
	@echo "clean           - Remove test artifacts"
	@echo "lint            - Run linting on all services"
	@echo "install         - Install dependencies for all services"
	@echo "build           - Build and push all Docker images"
	@echo "build-frontend  - Build frontend Docker images"
	@echo "deploy-staging  - Deploy to staging"
	@echo "deploy-prod     - Deploy to production"
	@echo "terraform-init  - Initialize Terraform"
	@echo "terraform-apply - Apply Terraform configuration"
	@echo "terraform-destroy - Destroy Terraform resources"

test:
	@echo "Installing core package in editable mode..."
	@pip install -e . --quiet
	@EXIT_STATUS=0; \
	for service in user-service chat-service itinerary-service destinations-service social-service travel-alerts-service; do \
		cd "services/$$service" && pytest --cov=app --cov-report=term-missing -q || EXIT_STATUS=$$?; \
		cd ../..; \
	done; \
	exit $$EXIT_STATUS

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -f .coverage services/.coverage services/*/.coverage 2>/dev/null || true
	@rm -f *-test-results.txt 2>/dev/null || true

lint:
	@for service in user-service chat-service itinerary-service destinations-service social-service travel-alerts-service; do \
		if [ -d "services/$$service" ]; then \
			(cd "services/$$service" && ruff check .) || true; \
		fi \
	done

install:
	@echo "Installing core package in editable mode..."
	@pip install -e .[all]
	@for service in user-service chat-service itinerary-service destinations-service social-service travel-alerts-service; do \
		if [ -f "services/$$service/requirements.txt" ]; then \
			pip install -r "services/$$service/requirements.txt"; \
		fi \
	done
	@if [ -f "services/frontend-service/package.json" ]; then \
		cd services/frontend-service && npm install; \
	fi

build:
	@./scripts/build/build-and-push-images.sh

build-frontend:
	@./scripts/build/build-frontend.sh

deploy-staging:
	@./scripts/deploy/deploy-staging.sh

deploy-prod:
	@./scripts/deploy/deploy-prod.sh

terraform-init:
	@./scripts/infra/init.sh

terraform-apply:
	@./scripts/infra/apply-all.sh

terraform-destroy:
	@./scripts/infra/destroy-all.sh
