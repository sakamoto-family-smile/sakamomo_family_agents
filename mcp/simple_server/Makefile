.PHONY: build run deploy

# Configuration
PROJECT_ID := your-project-id
REGION := asia-northeast1
IMAGE := simple-mcp-server
TAG := latest

# Build the Docker image
build:
	docker build -t $(IMAGE):$(TAG) .

# Run the server locally
run: build
	docker run -p 8080:8080 $(IMAGE):$(TAG)

# Deploy to Cloud Run
deploy: build
	# Tag the image for Google Container Registry
	docker tag $(IMAGE):$(TAG) gcr.io/$(PROJECT_ID)/$(IMAGE):$(TAG)

	# Push the image to Google Container Registry
	docker push gcr.io/$(PROJECT_ID)/$(IMAGE):$(TAG)

	# Deploy to Cloud Run
	gcloud run deploy $(IMAGE) \
		--image gcr.io/$(PROJECT_ID)/$(IMAGE):$(TAG) \
		--platform managed \
		--region $(REGION) \
		--allow-unauthenticated \
		--project $(PROJECT_ID)

# Run the client
client:
	python client.py