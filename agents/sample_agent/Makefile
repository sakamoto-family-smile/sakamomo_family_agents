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

# Docker commands
.PHONY: build
build:
	cd ../.. && docker build -t $(IMAGE_NAME):$(VERSION) -t $(REGISTRY)/$(IMAGE_NAME):$(VERSION) -f agents/sample_agent/Dockerfile .

.PHONY: run
run:
	docker run -p 8080:8080 -e GOOGLE_API_KEY=${GOOGLE_API_KEY} $(IMAGE_NAME):$(VERSION)

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
		--timeout 300 \
		--startup-probe-initial-delay 5 \
		--startup-probe-period 5 \
		--startup-probe-timeout 4 \
		--startup-probe-failure-threshold 3

# Test commands
.PHONY: test-docker
test-docker:
	./test/test_docker.sh

# Combined deployment command
.PHONY: deploy
deploy: build gcp-build-push gcp-run-deploy