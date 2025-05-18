# A2A Example UI

This is the UI component of the Agent2Agent example application. It provides a web interface for interacting with the A2A system.

## Requirements

- Python 3.13 or higher
- Dependencies listed in pyproject.toml
- Google Cloud Platform account and configured gcloud CLI
- Environment variables set in `.env` file:
  - GOOGLE_CLOUD_PROJECT
  - GOOGLE_API_KEY
  - GOOGLE_GENAI_USE_VERTEXAI

## Running the Application

The application can be run either directly with Python or using Docker.

### Local Development

```bash
# Build the Docker image
make build

# Run the container locally
make run

# Run local tests
make test-local

# Stop and remove local container
make clean
```

The application will be available at http://localhost:12000

### Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
make deploy

# After deployment, copy the Service URL from the output
# Example: https://a2a-ui-xxxxx.asia-northeast1.run.app

# Set the BASE_URL environment variable and run tests
export BASE_URL=<your-service-url> && make test-cloud-run

# Delete Cloud Run service
make clean-cloud-run
```

## Available Make Commands

- `make build`: Build Docker image locally
- `make push`: Push Docker image to Google Artifact Registry
- `make deploy`: Deploy the application to Cloud Run (includes build and push)
- `make run`: Run the container locally
- `make test-local`: Run tests against local container
- `make test-cloud-run`: Run tests against Cloud Run deployment
- `make clean`: Stop and remove local container
- `make clean-cloud-run`: Delete the Cloud Run service

## Environment Variables

The following environment variables should be set in your `.env` file:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_API_KEY=your-api-key
GOOGLE_GENAI_USE_VERTEXAI=true/false
```

For Cloud Run testing, you'll also need to set:

```bash
BASE_URL=your-cloud-run-service-url  # Required for make test-cloud-run
```
