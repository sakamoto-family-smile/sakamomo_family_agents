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

# Build the Docker image
echo "Building Docker image..."
cd "$PROJECT_ROOT"
echo "Building from directory: $(pwd)"
docker build -t sample-agent -f agents/sample_agent/Dockerfile .
cd - > /dev/null

# Run the container in the background
echo "Starting container..."
CONTAINER_ID=$(docker run -d -p 8080:8080 -e GOOGLE_API_KEY=${GOOGLE_API_KEY} sample-agent)

if [ -z "$CONTAINER_ID" ]; then
    echo "Error: Failed to start container"
    exit 1
fi

# Wait for the container to start
echo "Waiting for container to start..."
sleep 15

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