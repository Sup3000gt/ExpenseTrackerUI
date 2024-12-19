import logging
import requests
from appconfig import USER_BASE_API_URL, USER_SERVICE_SUBSCRIPTION_KEY

logger = logging.getLogger(__name__)


def login_user(username, password):
    """
    Perform user login and return success status, message, and token.
    """
    api_url = f"{USER_BASE_API_URL}/Users/login"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": USER_SERVICE_SUBSCRIPTION_KEY
    }
    payload = {"username": username, "password": password}

    try:
        logger.debug(f"Sending login request to {api_url} with username: {username}")
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            logger.info("Login successful.")
            try:
                response_data = response.json()
                logger.debug(f"Response data: {response_data}")
                return True, response_data, response_data.get("token")
            except ValueError as e:
                logger.error(f"Error parsing response JSON: {e}")
                return False, f"Error parsing response JSON: {e}", None
        logger.warning(f"Login failed with status code {response.status_code}: {response.text}")
        return False, response.text, None

    except Exception as e:
        logger.error(f"An error occurred during login: {e}")
        return False, f"Error: {e}", None
