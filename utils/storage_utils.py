import keyring

SERVICE_NAME = "ExpenseTrackerApp"  # Service name for keyring

def save_token(token):
    """Save the JWT token securely using keyring."""
    keyring.set_password(SERVICE_NAME, "jwt_token", token)

def load_token():
    """Load the JWT token securely from keyring."""
    return keyring.get_password(SERVICE_NAME, "jwt_token")

def delete_token():
    """Delete the JWT token from keyring."""
    keyring.delete_password(SERVICE_NAME, "jwt_token")
