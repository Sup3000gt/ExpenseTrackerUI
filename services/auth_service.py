import requests
from appconfig import USER_BASE_API_URL, USER_SERVICE_SUBSCRIPTION_KEY

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
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            print("Login successful")
            print(response.json())
            try:
                response_data = response.json()
                return True, response_data, response_data.get("token")
            except ValueError as e:
                return False, f"Error parsing response JSON: {e}", None
        return False, response.text, None

    except Exception as e:
        return False, f"Error: {e}", None
