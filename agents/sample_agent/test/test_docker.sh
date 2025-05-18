#!/bin/bash

# Load environment variables from .env
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found in $(pwd)"
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY is not set"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
cd ..
docker build -t sample-agent -f sample_agent/Dockerfile .
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
sleep 10

# Test the health endpoint
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)

if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo "Health check passed!"
else
    echo "Health check failed with status code: $HEALTH_RESPONSE"
    echo "Container logs:"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    exit 1
fi

# Test the agent capabilities endpoint
echo "Testing agent capabilities..."
CAPABILITIES_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/agent-card)

if [ "$CAPABILITIES_RESPONSE" == "200" ]; then
    echo "Capabilities check passed!"
else
    echo "Capabilities check failed with status code: $CAPABILITIES_RESPONSE"
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