import jwt
import time

def is_token_valid(token):
    """Check if the JWT token is valid and not expired."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})  # Decode without verification
        expiration = decoded.get("exp")
        if expiration and expiration > time.time():
            return True
        return False
    except jwt.ExpiredSignatureError:
        return False
    except jwt.DecodeError:
        return False

def decode_token(token):
    """Decode a JWT token to extract information."""
    try:
        return jwt.decode(token, options={"verify_signature": False})  # Decode without verification
    except jwt.DecodeError:
        return None
