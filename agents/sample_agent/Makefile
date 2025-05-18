# Load environment variables from .env
ifneq (,$(wildcard .env))
include .env
endif

# Configuration
PROJECT_ID ?= $(GCP_PROJECT_ID)
REGION := asia-northeast1
SERVICE_NAME := sample-agent
IMAGE_NAME := sample-agent
VERSION := v1
AR_REGISTRY_NAME := sakamomo-family-service
REGISTRY := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(AR_REGISTRY_NAME)/agents

# Get the Cloud Run service URL
SERVICE_URL := $(shell gcloud run services describe $(SERVICE_NAME) --region $(REGION) --format='value(status.url)')

# Docker commands
.PHONY: build
build:
	cd ../.. && docker build -t $(IMAGE_NAME):$(VERSION) -t $(REGISTRY)/$(IMAGE_NAME):$(VERSION) -f agents/sample_agent/Dockerfile .

.PHONY: run
run:
	docker run -p 10002:8080 -e GOOGLE_API_KEY=${GOOGLE_API_KEY} $(IMAGE_NAME):$(VERSION)

# GCP commands
.PHONY: gcp-configure
gcp-configure:
	gcloud config set project $(PROJECT_ID)
	gcloud config set run/region $(REGION)
	gcloud auth configure-docker $(REGION)-docker.pkg.dev
	-gcloud artifacts repositories create sample-agent --repository-format=docker \
		--location=$(REGION) --description="Repository for sample agent"

.PHONY: gcp-build-push
gcp-build-push:
	docker push $(REGISTRY)/$(IMAGE_NAME):$(VERSION)

.PHONY: gcp-run-deploy
gcp-run-deploy:
	gcloud run deploy $(SERVICE_NAME) \
		--image $(REGISTRY)/$(IMAGE_NAME):$(VERSION) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--set-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY} \
		--memory 512Mi \
		--cpu 1 \
		--min-instances 0 \
		--max-instances 10 \
		--port 8080 \
		--timeout 300

# Test commands
.PHONY: test-docker
test-docker:
	./test/test_docker.sh

# Verification commands
.PHONY: verify-agent-info
verify-agent-info:
	@echo "Checking agent info at $(SERVICE_URL)/.well-known/agent.json"
	@curl -f $(SERVICE_URL)/.well-known/agent.json || (echo "\nAgent info check failed!" && exit 1)
	@echo "\nAgent info check passed!"

.PHONY: verify-api
verify-api:
	@echo "Testing reimbursement API at $(SERVICE_URL)"
	@curl -X POST \
		-H "Content-Type: application/json" \
		-d '{"jsonrpc": "2.0", "method": "tasks/send", "id": "test-1", "params": {"id": "test-1", "sessionId": "test-session", "message": {"role": "user", "parts": [{"type": "text", "text": "Can you reimburse me $20 for my lunch with the clients?"}]}, "acceptedOutputModes": ["text"]}}' \
		$(SERVICE_URL)
	@echo "\nAPI test completed!"

.PHONY: verify-all
verify-all: verify-agent-info verify-api

# Combined deployment command
.PHONY: deploy
deploy: build gcp-build-push gcp-run-deploy