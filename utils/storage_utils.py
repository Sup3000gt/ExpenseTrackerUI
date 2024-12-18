import keyring

SERVICE_NAME = "ExpenseTrackerApp"  # Service name for keyring

def save_token(token):
    """Save the JWT token securely using keyring."""
    keyring.set_password(SERVICE_NAME, "jwt_token", token)
    print("Token saved successfully.")

def load_token():
    """Load the JWT token securely from keyring."""
    token = keyring.get_password(SERVICE_NAME, "jwt_token")
    print(f"Loaded token: {token}")
    return token

def delete_token():
    """Delete the JWT token from keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, "jwt_token")
        print("Token deleted successfully.")
    except keyring.errors.PasswordDeleteError:
        print("No token to delete.")