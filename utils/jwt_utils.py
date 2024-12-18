import jwt
import time

def is_token_valid(token):
    """Check if the JWT token is valid and not expired."""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})  # Decode without verification
        expiration = decoded.get("exp")
        print(f"Token expiration: {expiration}, Current time: {time.time()}")
        if expiration and expiration > time.time():
            return True
        print("Token has expired.")
        return False
    except jwt.ExpiredSignatureError:
        print("Token has expired (ExpiredSignatureError).")
        return False
    except jwt.DecodeError:
        print("Failed to decode token.")
        return False

def decode_token(token):
    """Decode a JWT token to extract information."""
    try:
        return jwt.decode(token, options={"verify_signature": False})  # Decode without verification
    except jwt.DecodeError:
        return None
