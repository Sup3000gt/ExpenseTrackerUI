import requests
from appconfig import BASE_API_URL, SUBSCRIPTION_KEY

def register_user(data):
    """
    Register a new user using the provided data.

    Args:
        data (dict): A dictionary containing user details like username, passwordHash, email, etc.

    Returns:
        tuple: (success: bool, message: str)
    """
    api_url = f"{BASE_API_URL}/Users/register"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            return True, "Registration Successful"
        return False, f"Error: {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {e}"
