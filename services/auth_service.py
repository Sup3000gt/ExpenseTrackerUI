import requests
from appconfig import USER_BASE_API_URL, SUBSCRIPTION_KEY

def login_user(username, password):
    """
    Perform user login and return success status, message, and token.
    """
    api_url = f"{USER_BASE_API_URL}/Users/login"
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY  # Include the subscription key
    }
    payload = {"username": username, "password": password}

    try:
        # Log the payload and headers for debugging
        print(f"Sending payload: {payload}")
        print(f"Headers: {headers}")

        response = requests.post(api_url, headers=headers, json=payload)

        # Log the response for debugging
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            # Handle plain text response
            if response.text.strip().lower() == "login successful.":
                return True, "Login Successful", None  # No token provided
            else:
                # Attempt to parse as JSON if necessary
                token = response.json().get("token")
                return True, "Login Successful", token
        return False, f"Error: {response.text}", None
    except Exception as e:
        return False, f"Error: {e}", None
