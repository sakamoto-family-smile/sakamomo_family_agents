import requests
import sys
import logging
import os
from google.cloud import run_v2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_cloud_run_url():
    """Get the URL of the Cloud Run service."""
    client = run_v2.ServicesClient()
    project_id = os.getenv("GCP_PROJECT")
    region = "asia-northeast1"
    service_name = "asset-securities-report-agent"

    request = run_v2.GetServiceRequest(
        name=f"projects/{project_id}/locations/{region}/services/{service_name}"
    )

    try:
        response = client.get_service(request=request)
        return response.uri
    except Exception as e:
        logger.error(f"Failed to get Cloud Run URL: {e}")
        return None


def test_health_check(base_url):
    """Test the agent card endpoint of the Cloud Run service."""
    url = f"{base_url}/.well-known/agent.json"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            agent_card = response.json()
            if agent_card.get("name") == "Asset Securities Report":
                logger.info("Agent card check passed!")
                return True
            else:
                logger.error("Agent card check failed: unexpected agent name")
                return False
        else:
            logger.error(
                f"Agent card check failed with status code: {response.status_code}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Agent card check failed with error: {e}")
        return False


def test_api_functionality(base_url):
    """Test the main API functionality with a sample request."""
    url = f"{base_url}/"
    test_data = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "id": "test-request-id",
        "params": {
            "id": "test-task-id",
            "sessionId": "test-session-id",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "Please analyze ACCESS Co., Ltd.'s annual securities report."
                    }
                ]
            },
            "acceptedOutputModes": ["text", "text/plain"]
        }
    }

    try:
        response = requests.post(url, json=test_data)
        if response.status_code == 200:
            logger.info("API functionality test passed!")
            return True
        else:
            logger.error(
                f"API functionality test failed with status code: {response.status_code}"
            )
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"API functionality test failed with error: {e}")
        return False


def main():
    """Main test function."""
    logger.info("Starting Cloud Run tests...")

    # Get Cloud Run URL
    base_url = get_cloud_run_url()
    if not base_url:
        logger.error("Failed to get Cloud Run URL")
        sys.exit(1)

    # Test health check
    if not test_health_check(base_url):
        logger.error("Health check test failed")
        sys.exit(1)

    # Test API functionality
    if not test_api_functionality(base_url):
        logger.error("API functionality test failed")
        sys.exit(1)

    logger.info("All Cloud Run tests passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()