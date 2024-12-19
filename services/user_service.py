import logging
import requests
from appconfig import USER_BASE_API_URL, USER_SERVICE_SUBSCRIPTION_KEY

logger = logging.getLogger(__name__)


def register_user(data):
    """
    Register a new user using the provided data.

    Args:
        data (dict): A dictionary containing user details like username, passwordHash, email, etc.

    Returns:
        tuple: (success: bool, message: str)
    """
    api_url = f"{USER_BASE_API_URL}/Users/register"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": USER_SERVICE_SUBSCRIPTION_KEY
    }

    try:
        logger.debug(f"Sending registration request to {api_url} with data: {data}")
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info("User registration successful.")
            return True, "Registration Successful"
        logger.warning(f"User registration failed with status code {response.status_code}: {response.text}")
        return False, f"Error: {response.text}"
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during user registration: {e}")
        return False, f"Error: {e}"
