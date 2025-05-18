# Load environment variables from .env
ifneq (,$(wildcard .env))
include .env
endif

# Configuration
PROJECT_ID ?= $(GCP_PROJECT_ID)
REGION := asia-northeast1
SERVICE_NAME := sample-agent
IMAGE_NAME := sample-agent

# Docker commands
.PHONY: build
build:
	cd ../.. && docker build -t $(IMAGE_NAME) -f agents/sample_agent/Dockerfile agents/sample_agent

.PHONY: run
run:
	docker run -p 8080:8080 -e GOOGLE_API_KEY=${GOOGLE_API_KEY} $(IMAGE_NAME)

# GCP commands
.PHONY: gcp-configure
gcp-configure:
	gcloud config set project $(PROJECT_ID)
	gcloud config set run/region $(REGION)

.PHONY: gcp-build-push
gcp-build-push:
	docker tag $(IMAGE_NAME) gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE_NAME)

.PHONY: gcp-run-deploy
gcp-run-deploy:
	gcloud run deploy $(SERVICE_NAME) \
		--image gcr.io/$(PROJECT_ID)/$(IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--set-env-vars GOOGLE_API_KEY=${GOOGLE_API_KEY}

# Test commands
.PHONY: test-docker
test-docker:
	./test/test_docker.sh

# Combined deployment command
.PHONY: deploy
deploy: build gcp-configure gcp-build-push gcp-run-deploy