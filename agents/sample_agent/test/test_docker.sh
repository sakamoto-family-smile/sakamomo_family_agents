#!/bin/bash

# Get the absolute path of the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# Load environment variables from .env
if [ -f "${SCRIPT_DIR}/../.env" ]; then
    source "${SCRIPT_DIR}/../.env"
else
    echo "Error: .env file not found in ${SCRIPT_DIR}/.."
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set"
    exit 1
fi

# Set version
VERSION="v1"
IMAGE_NAME="sample-agent:${VERSION}"

# Build the Docker image
echo "Building Docker image ${IMAGE_NAME}..."
cd "$PROJECT_ROOT"
echo "Building from directory: $(pwd)"
docker build -t ${IMAGE_NAME} -f agents/sample_agent/Dockerfile .
cd - > /dev/null

# Run the container in the background
echo "Starting container..."
CONTAINER_ID=$(docker run -d -p 8080:8080 -e GOOGLE_API_KEY=${GOOGLE_API_KEY} ${IMAGE_NAME})

if [ -z "$CONTAINER_ID" ]; then
    echo "Error: Failed to start container"
    exit 1
fi

# Function to check health endpoint
check_health() {
    local max_attempts=30
    local attempt=1
    local wait_time=2

    echo "Checking health endpoint..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:8080/health > /dev/null; then
            echo "Health check passed on attempt $attempt"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: Health check failed, waiting ${wait_time}s..."
        sleep $wait_time
        attempt=$((attempt + 1))
    done

    echo "Health check failed after $max_attempts attempts"
    return 1
}

# Wait for the container to be healthy
if ! check_health; then
    echo "Container failed to become healthy"
    echo "Container logs:"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    exit 1
fi

# Test the agent capabilities endpoint
echo "Testing agent capabilities..."
RESPONSE=$(curl -s http://localhost:8080/agent-card)

if [ $? -eq 0 ] && [ ! -z "$RESPONSE" ]; then
    echo "Agent capabilities test passed!"
    echo "Response: $RESPONSE"
else
    echo "Agent capabilities test failed"
    echo "Container logs:"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    exit 1
fi

# Stop the container
echo "Stopping container..."
docker stop $CONTAINER_ID

echo "All tests passed successfully!"
exit 0