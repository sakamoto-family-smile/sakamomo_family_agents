# Sample Agent

This is a sample Google ADK-based Expense Reimbursement agent hosted as an A2A server.

## Prerequisites

- Python 3.12 or higher
- Docker
- Google Cloud SDK
- Make

## Environment Setup

1. Create a `.env` file in the project root with the following variables:
```
GOOGLE_API_KEY=your_google_api_key
GCP_PROJECT_ID=your_gcp_project_id
```

2. Install dependencies:
```bash
pip install -e .
```

## Local Development

To run the agent locally:
```bash
python -m sample_agent
```

## Docker Development

### Build and Run Locally
```bash
# Build the Docker image
make build

# Run the container locally
make run
```

### Test Docker Environment
To verify the Docker environment is working correctly:
```bash
make test-docker
```

This will:
- Build the Docker image
- Start the container
- Test the health endpoint
- Test the agent capabilities endpoint
- Stop the container

## Cloud Run Deployment

### Prerequisites
1. Ensure you have the Google Cloud SDK installed and configured
2. Make sure you have the necessary permissions to deploy to Cloud Run
3. Set up your `.env` file with the required environment variables

### Deployment Steps
```bash
# Deploy to Cloud Run
make deploy
```

This will:
1. Build the Docker image
2. Configure GCP settings
3. Push the image to Google Container Registry
4. Deploy to Cloud Run

### Manual Deployment Steps
If you prefer to deploy manually, you can use the following commands:

1. Configure GCP:
```bash
make gcp-configure
```

2. Build and push the image:
```bash
make gcp-build-push
```

3. Deploy to Cloud Run:
```bash
make gcp-run-deploy
```

## Environment Variables

- `GOOGLE_API_KEY`: Required for Google ADK functionality
- `GCP_PROJECT_ID`: Your Google Cloud Project ID

## API Endpoints

- `/health`: Health check endpoint
- `/agent-card`: Returns agent capabilities and information
- `/`: Main endpoint for agent interaction

## Troubleshooting

If you encounter any issues:

1. Check the logs:
```bash
# For local Docker container
docker logs <container_id>

# For Cloud Run
gcloud run services logs tail sample-agent
```

2. Verify environment variables are set correctly
3. Ensure all prerequisites are installed and configured properly
