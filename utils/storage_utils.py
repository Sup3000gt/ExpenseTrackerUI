import keyring
import logging

SERVICE_NAME = "ExpenseTrackerApp"  # Service name for keyring

logger = logging.getLogger(__name__)


def save_token(token):
    """Save the JWT token securely using keyring."""
    keyring.set_password(SERVICE_NAME, "jwt_token", token)
    logger.info("Token saved successfully.")


def load_token():
    """Load the JWT token securely from keyring."""
    token = keyring.get_password(SERVICE_NAME, "jwt_token")
    logger.debug(f"Loaded token: {token}")
    return token


def delete_token():
    """Delete the JWT token from keyring."""
    try:
        keyring.delete_password(SERVICE_NAME, "jwt_token")
        logger.info("Token deleted successfully.")
    except keyring.errors.PasswordDeleteError:
        logger.warning("No token to delete.")
