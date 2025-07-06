.PHONY: build push deploy test test-cov

# Configuration
PROJECT_ID := $(shell gcloud config get-value project)
REGION := asia-northeast1
REPOSITRY_NAME ?= sakamomo-family-mcp
IMAGE_NAME := bigquery-mcp-server
ARTIFACT_REGISTRY_HOST_NAME ?= ${REGION}-docker.pkg.dev
TAG := latest

# Full image path
IMAGE := ${ARTIFACT_REGISTRY_HOST_NAME}/$(PROJECT_ID)/${REPOSITRY_NAME}/$(IMAGE_NAME):$(TAG)

build:
	docker build -t $(IMAGE) .

push: build
	docker push $(IMAGE)

deploy: push
	gcloud run deploy $(IMAGE_NAME) \
		--image $(IMAGE) \
		--region $(REGION) \
		--platform managed \
		--allow-unauthenticated \
		--set-env-vars "GOOGLE_CLOUD_PROJECT=$(PROJECT_ID)" \
		--service-account "bigquery-mcp-server@$(PROJECT_ID).iam.gserviceaccount.com"

# Local development
run-local:
	python -m bigquery_server.server

# Docker local development
run-docker: build
	docker run -p 8080:8080 \
		-e GOOGLE_CLOUD_PROJECT=$(PROJECT_ID) \
		-v $(PWD)/../../service_account.json:/app/service_account.json \
		-e GOOGLE_APPLICATION_CREDENTIALS=/app/service_account.json \
		$(IMAGE)

# Testing
test:
	pytest src/bigquery_server/tests/

test-cov:
	pytest src/bigquery_server/tests/ --cov=src/bigquery_server --cov-report=term-missing

# Create service account and grant permissions
setup-sa:
	gcloud iam service-accounts create bigquery-mcp-server \
		--display-name "BigQuery MCP Server"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member "serviceAccount:bigquery-mcp-server@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role "roles/bigquery.dataViewer"
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member "serviceAccount:bigquery-mcp-server@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role "roles/bigquery.jobUser"