import requests

REGISTER_API_URL = "https://expenseuserserviceapi.azure-api.net/api/Users/register"
SUBSCRIPTION_KEY = "49630d64dd954e64b06992eade60a44e"


def register_user(data):
    """
    Register a new user using the provided data.

    Args:
        data (dict): A dictionary containing user details like username, passwordHash, email, etc.

    Returns:
        tuple: (success: bool, message: str)
    """
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }
    try:
        response = requests.post(REGISTER_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return True, "Registration Successful"
        return False, f"Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {e}"
