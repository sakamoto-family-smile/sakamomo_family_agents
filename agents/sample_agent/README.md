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

By default, the agent will listen on `0.0.0.0:8080`. You can customize the host and port using environment variables:
```bash
HOST=localhost PORT=10002 python -m sample_agent
```

## Docker Development

### Build and Run Locally
```bash
# Build the Docker image
make build

# Run the container locally
# This will map port 10002 on your host to port 8080 in the container
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
- Run the test suite
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
2. Push the image to Google Artifact Registry
3. Deploy to Cloud Run

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

### Verify Deployment
After deployment, you can verify the service is working correctly:

```bash
# Check agent information
make verify-agent-info

# Test the API
make verify-api

# Run all verification checks
make verify-all
```

## Environment Variables

- `GOOGLE_API_KEY`: Required for Google ADK functionality
- `GCP_PROJECT_ID`: Your Google Cloud Project ID
- `HOST`: Host to bind to (default: "0.0.0.0")
- `PORT`: Port to listen on (default: "8080")

## API Endpoints

- `/.well-known/agent.json`: Returns agent capabilities and information (GET)
- `/`: Main endpoint for agent interaction (POST)
  - Accepts JSON-RPC 2.0 requests
  - Supported methods:
    - `tasks/send`: Send a task to the agent
    - `tasks/get`: Get task status
    - `tasks/cancel`: Cancel a task
    - `tasks/sendSubscribe`: Send a task with streaming response

### Example API Request

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tasks/send",
    "id": "test-1",
    "params": {
      "id": "test-1",
      "sessionId": "test-session",
      "message": {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Can you reimburse me $20 for my lunch with the clients?"
          }
        ]
      },
      "acceptedOutputModes": ["text"]
    }
  }' \
  http://localhost:10002
```

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
4. Check the service URL and endpoints:
```bash
# Get the Cloud Run service URL
gcloud run services describe sample-agent --region asia-northeast1 --format='value(status.url)'
```
