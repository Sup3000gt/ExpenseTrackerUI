import jwt
import time
import logging

logger = logging.getLogger(__name__)


def is_token_valid(token):
    """Check if the JWT token is valid and not expired."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        expiration = decoded.get("exp")
        logger.debug(f"Token expiration: {expiration}, Current time: {time.time()}")
        if expiration and expiration > time.time():
            return True
        logger.info("Token has expired.")
        return False
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired (ExpiredSignatureError).")
        return False
    except jwt.DecodeError:
        logger.error("Failed to decode token.")
        return False


def decode_token(token):
    """Decode a JWT token to extract information."""
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.DecodeError:
        logger.error("Failed to decode token.")
        return None
