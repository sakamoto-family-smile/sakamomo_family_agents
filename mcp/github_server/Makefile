# GitHub MCP Server GCP Deployment Makefile
#
# This Makefile provides commands to deploy the GitHub MCP Server to Google Cloud Platform
# using Cloud Run for serverless deployment.

# Configuration variables
PROJECT_ID ?= $(shell gcloud config get-value project)
REGION ?= asia-northeast1
SERVICE_NAME ?= github-mcp-server
REPOSITRY_NAME ?= sakamomo-family-mcp
ARTIFACT_REGISTRY_HOST_NAME ?= ${REGION}-docker.pkg.dev
GCP_IMAGE_NAME ?= ${ARTIFACT_REGISTRY_HOST_NAME}/$(PROJECT_ID)/${REPOSITRY_NAME}/$(SERVICE_NAME)
DOCKER_IMAGE ?= ghcr.io/github/github-mcp-server:latest
SERVICE_ACCOUNT_NAME ?= github-mcp-server-sa
SERVICE_ACCOUNT_EMAIL ?= $(SERVICE_ACCOUNT_NAME)@$(PROJECT_ID).iam.gserviceaccount.com

# Load environment variables from .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Default target
.PHONY: help
help: ## Show this help message
	@echo "GitHub MCP Server GCP Deployment"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: check-prerequisites
check-prerequisites: ## Check if required tools are installed
	@echo "Checking prerequisites..."
	@command -v gcloud >/dev/null 2>&1 || { echo "gcloud CLI is required but not installed. Please install Google Cloud SDK."; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed."; exit 1; }
	@echo "✓ All prerequisites are satisfied"

.PHONY: auth
auth: ## Authenticate with Google Cloud
	@echo "Authenticating with Google Cloud..."
	gcloud auth login
	gcloud config set project $(PROJECT_ID)
	gcloud auth configure-docker ${ARTIFACT_REGISTRY_HOST_NAME}

.PHONY: enable-apis
enable-apis: ## Enable required Google Cloud APIs
	@echo "Enabling required APIs..."
	gcloud services enable run.googleapis.com
	gcloud services enable containerregistry.googleapis.com
	gcloud services enable cloudbuild.googleapis.com

.PHONY: pull-image
pull-image: ## Pull the GitHub MCP Server Docker image
	@echo "Pulling GitHub MCP Server Docker image..."
	docker pull $(DOCKER_IMAGE)

.PHONY: tag-image
tag-image: ## Tag the Docker image for GCP Container Registry
	@echo "Tagging Docker image for GCP..."
	docker tag $(DOCKER_IMAGE) $(GCP_IMAGE_NAME)

.PHONY: push-image
push-image: ## Push the Docker image to GCP Container Registry
	@echo "Pushing Docker image to GCP Container Registry..."
	docker push $(GCP_IMAGE_NAME)

.PHONY: create-service-account
create-service-account: ## Create and setup service account for Cloud Run
	@echo "Creating service account for Cloud Run..."
	gcloud iam service-accounts create $(SERVICE_ACCOUNT_NAME) \
		--display-name="GitHub MCP Server Service Account" \
		--description="Service account for GitHub MCP Server running on Cloud Run"
	@echo "Granting necessary roles to service account..."
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SERVICE_ACCOUNT_EMAIL)" \
		--role="roles/secretmanager.secretAccessor"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SERVICE_ACCOUNT_EMAIL)" \
		--role="roles/run.invoker"

.PHONY: deploy
deploy: pull-image tag-image push-image ## Deploy the GitHub MCP Server to Cloud Run
	@echo "Deploying GitHub MCP Server to Cloud Run..."
	@if [ -z "$(GITHUB_TOKEN)" ]; then echo "Error: GITHUB_TOKEN is not set. Please create a .env file with your GitHub token."; exit 1; fi
	gcloud run deploy $(SERVICE_NAME) \
		--image $(GCP_IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--service-account $(SERVICE_ACCOUNT_EMAIL) \
		--allow-unauthenticated \
		--port 8080 \
		--memory 512Mi \
		--cpu 1 \
		--max-instances 10 \
		--set-env-vars "GITHUB_PERSONAL_ACCESS_TOKEN=$(GITHUB_TOKEN)" \
		--set-env-vars "GITHUB_APP_ID=$(GITHUB_APP_ID)" \
		--set-env-vars "GITHUB_APP_PRIVATE_KEY=$(GITHUB_APP_PRIVATE_KEY)"

.PHONY: deploy-with-secret
deploy-with-secret: pull-image tag-image push-image ## Deploy with GitHub secrets from Secret Manager
	@echo "Deploying with GitHub secrets from Secret Manager..."
	gcloud run deploy $(SERVICE_NAME) \
		--image $(GCP_IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--service-account $(SERVICE_ACCOUNT_EMAIL) \
		--allow-unauthenticated \
		--port 8080 \
		--memory 512Mi \
		--cpu 1 \
		--max-instances 10 \
		--set-env-vars "GITHUB_PERSONAL_ACCESS_TOKEN=$(GITHUB_TOKEN)" \
		--set-env-vars "GITHUB_APP_ID=$(GITHUB_APP_ID)" \
		--set-env-vars "GITHUB_APP_PRIVATE_KEY=$(GITHUB_APP_PRIVATE_KEY)"

.PHONY: create-secrets
create-secrets: check-env ## Create secrets in Secret Manager (requires .env file with GITHUB_TOKEN, GITHUB_APP_ID, GITHUB_APP_PRIVATE_KEY)
	@echo "Creating secrets in Secret Manager..."
	@if [ -z "$(GITHUB_TOKEN)" ]; then echo "Error: GITHUB_TOKEN is not set. Please create a .env file with your GitHub token."; exit 1; fi
	@if [ -z "$(GITHUB_APP_ID)" ]; then echo "Warning: GITHUB_APP_ID is not set, skipping..."; fi
	@if [ -z "$(GITHUB_APP_PRIVATE_KEY)" ]; then echo "Warning: GITHUB_APP_PRIVATE_KEY is not set, skipping..."; fi
	echo "$(GITHUB_TOKEN)" | gcloud secrets create github-token --data-file=-
	@if [ -n "$(GITHUB_APP_ID)" ]; then echo "$(GITHUB_APP_ID)" | gcloud secrets create github-app-id --data-file=-; fi
	@if [ -n "$(GITHUB_APP_PRIVATE_KEY)" ]; then echo "$(GITHUB_APP_PRIVATE_KEY)" | gcloud secrets create github-app-private-key --data-file=-; fi

.PHONY: get-url
get-url: ## Get the Cloud Run service URL
	@echo "Getting service URL..."
	@gcloud run services describe $(SERVICE_NAME) --region=$(REGION) --format="value(status.url)"

.PHONY: logs
logs: ## View Cloud Run service logs
	@echo "Viewing service logs..."
	gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=$(SERVICE_NAME)" --limit=50

.PHONY: delete
delete: ## Delete the Cloud Run service
	@echo "Deleting Cloud Run service..."
	gcloud run services delete $(SERVICE_NAME) --region=$(REGION) --quiet

.PHONY: clean
clean: ## Clean up Docker images
	@echo "Cleaning up Docker images..."
	docker rmi $(DOCKER_IMAGE) $(IMAGE_NAME) 2>/dev/null || true

.PHONY: status
status: ## Check the status of the Cloud Run service
	@echo "Checking service status..."
	gcloud run services describe $(SERVICE_NAME) --region=$(REGION) --format="table(status.conditions[0].type,status.conditions[0].status,status.url)"

# Development and testing targets
.PHONY: test-local
test-local: check-env ## Test the GitHub MCP Server locally
	@echo "Testing GitHub MCP Server locally..."
	@if [ -z "$(GITHUB_TOKEN)" ]; then echo "Error: GITHUB_TOKEN is not set. Please create a .env file with your GitHub token."; exit 1; fi
	docker run --rm -p 8080:8080 \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-e GITHUB_APP_ID=$(GITHUB_APP_ID) \
		-e GITHUB_APP_PRIVATE_KEY=$(GITHUB_APP_PRIVATE_KEY) \
		$(DOCKER_IMAGE)

.PHONY: build-local
build-local: ## Build a local Docker image for testing
	@echo "Building local Docker image..."
	docker build -t $(SERVICE_NAME)-local -f Dockerfile.local .

# Configuration targets
.PHONY: setup-env
setup-env: ## Create a .env file template
	@echo "Creating .env file template..."
	@echo "# GitHub MCP Server Environment Configuration" > .env.template
	@echo "# Copy this file to .env and fill in your values" >> .env.template
	@echo "" >> .env.template
	@echo "# GitHub Personal Access Token (required)" >> .env.template
	@echo "# Get this from: https://github.com/settings/tokens" >> .env.template
	@echo "# Required scopes: repo, workflow (for GitHub Actions access)" >> .env.template
	@echo "GITHUB_TOKEN=your_github_token_here" >> .env.template
	@echo "" >> .env.template
	@echo "# GitHub App Configuration (optional, for enhanced permissions)" >> .env.template
	@echo "# Only needed if you're using GitHub Apps instead of Personal Access Tokens" >> .env.template
	@echo "# If using GitHub Apps, you'll need to create a GitHub App and get these values" >> .env.template
	@echo "GITHUB_APP_ID=your_github_app_id_here" >> .env.template
	@echo "GITHUB_APP_PRIVATE_KEY=your_github_app_private_key_here" >> .env.template
	@echo "" >> .env.template
	@echo "# GCP Configuration (optional, will use gcloud config defaults if not set)" >> .env.template
	@echo "# These values will be automatically detected from gcloud config if not specified" >> .env.template
	@echo "PROJECT_ID=$(PROJECT_ID)" >> .env.template
	@echo "REGION=$(REGION)" >> .env.template
	@echo "SERVICE_NAME=$(SERVICE_NAME)" >> .env.template
	@echo ".env template created at .env.template"
	@echo "Copy .env.template to .env and fill in your values:"
	@echo "  cp .env.template .env"
	@echo "  # Edit .env with your actual values"

.PHONY: check-env
check-env: ## Check if .env file exists and has required values
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Run 'make setup-env' to create a template."; \
		exit 1; \
	fi
	@echo "✓ .env file found"
	@if [ -z "$(GITHUB_TOKEN)" ]; then \
		echo "Warning: GITHUB_TOKEN is not set in .env file"; \
	else \
		echo "✓ GITHUB_TOKEN is set"; \
	fi