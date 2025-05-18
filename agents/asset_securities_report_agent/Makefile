# Load environment variables from .env file
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Variables
PROJECT_ID := $(GCP_PROJECT)
REGION := asia-northeast1
AR_REGISTRY_NAME := sakamomo-family-service
IMAGE_NAME := asset-securities-report-agent
TAG := latest
SERVICE_NAME := asset-securities-report-agent

# Full image path
FULL_IMAGE_NAME := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(AR_REGISTRY_NAME)/agents/$(IMAGE_NAME):$(TAG)

.PHONY: build push deploy run test test-local test-cloud-run clean clean-cloud-run

# Build Docker image
build:
	cd ../.. && docker build -t $(IMAGE_NAME):$(TAG) -f agents/asset_securities_report_agent/Dockerfile .

# Push to Artifact Registry
push: build
	docker tag $(IMAGE_NAME):$(TAG) $(FULL_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)

# Deploy to Cloud Run
deploy: push
	gcloud run deploy $(SERVICE_NAME) \
		--image $(FULL_IMAGE_NAME) \
		--platform managed \
		--region $(REGION) \
		--port 10020 \
		--allow-unauthenticated

# Run container locally
run:
	docker run -d -p 10020:10020 \
		-e GOOGLE_API_KEY=${GOOGLE_API_KEY} \
		-e EDINET_API_KEY=${EDINET_API_KEY} \
		-e GCP_PROJECT=${GCP_PROJECT} \
		-e GCS_LOG_BUCKET_NAME=${GCS_LOG_BUCKET_NAME} \
		-e LLM_MODEL_NAME=${LLM_MODEL_NAME} \
		--name $(IMAGE_NAME) $(IMAGE_NAME):$(TAG)

# Test local container
test-local:
	python tests/test_local.py

# Test Cloud Run deployment
test-cloud-run:
	python tests/test_cloud_run.py

# Stop and remove local container
clean:
	docker stop $(IMAGE_NAME) || true
	docker rm $(IMAGE_NAME) || true

# Delete Cloud Run service
clean-cloud-run:
	gcloud run services delete $(SERVICE_NAME) \
		--platform managed \
		--region $(REGION) \
		--quiet