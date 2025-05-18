import requests
import sys
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_health_check():
    """Test if the UI application is running."""
    url = "http://localhost:12000"
    max_retries = 5
    retry_delay = 2

    for i in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logger.info("Health check passed!")
                return True
            else:
                logger.error(
                    f"Health check failed with status code: {response.status_code}"
                )
                return False
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                logger.warning(
                    f"Connection failed. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Health check failed.")
                return False
    return False


def test_api_functionality():
    """Test the API endpoints."""
    url = "http://localhost:12000/agents/list"

    try:
        response = requests.post(url)
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
    logger.info("Starting local container tests...")

    # Test health check
    if not test_health_check():
        logger.error("Health check test failed")
        sys.exit(1)

    # Test API functionality
    if not test_api_functionality():
        logger.error("API functionality test failed")
        sys.exit(1)

    logger.info("All tests passed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()