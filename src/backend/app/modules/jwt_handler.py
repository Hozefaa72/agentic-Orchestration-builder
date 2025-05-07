import time
from typing import Dict
import jwt
from backend.app.config.config import Settings
from jwt import ExpiredSignatureError, InvalidTokenError
import uuid


def generate_session_id() -> str:

    return str(uuid.uuid4())


def token_response(token: str):
    """
    Create a dictionary response containing the access token.

    Args:
        token (str): The access token.

    Returns:
        dict: A dictionary response with the access token.

    """
    return {"access_token": token}


secret_key = Settings().SECRET_KEY


def sign_jwt(user_id: str) -> Dict[str, str]:
    """
    Sign a JWT token for the given user ID.

    Args:
        user_id (str): The user ID to include in the JWT payload.

    Returns:
        Dict[str, str]: A dictionary response containing the access token.

    """

    session_id = generate_session_id()
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "expires": time.time() + 86400,
    }
    return token_response(jwt.encode(payload, secret_key, algorithm="HS256"))


def update_jwt(user_id: str, thread_id: str, session_id: str) -> Dict[str, str]:
    """
    Sign a JWT token for the given user ID.

    Args:
        user_id (str): The user ID to include in the JWT payload.

    Returns:
        Dict[str, str]: A dictionary response containing the access token.

    """

    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "thread_id": thread_id,
        "expires": time.time() + 86400,
    }
    return token_response(jwt.encode(payload, secret_key, algorithm="HS256"))


def decode_jwt(token: str) -> dict:
    """
    Decode a JWT token and return the decoded payload if the token is valid.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded JWT payload if the token is valid, None if invalid or expired.
    """
    try:

        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        if "expires" in decoded_token and decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return None

    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
        return None
    except Exception as e:

        print(f"Error decoding token: {e}")
        return None
