from fastapi import HTTPException, status
import time
import jwt
from app.utils.config import ENV_PROJECT
import uuid
from datetime import datetime, timedelta, timezone
import secrets


def generate_session_id():
    try:
        session_id = str(uuid.uuid4())
        if not session_id:
            raise ValueError("Failed to generate a valid UUID")
        return session_id

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate session ID")


def token_response(token: str):
    try:
        if not token or not isinstance(token, str):
            raise HTTPException(status_code=422, detail="Invalid token")
        token = "Bearer" + " " + token
        return {"access_token": token}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating token response")


secret_key = ENV_PROJECT.SECRET_KEY


def sign_jwt(user_id: str):
    try:
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(status_code=422, detail="Invalid user ID for JWT")
        session_id = generate_session_id()
        print("session id", session_id)
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "expires": time.time()
            + (
                ENV_PROJECT.GUEST_TOKEN_EXPIRY_DAYS
                * ENV_PROJECT.GUEST_TOKEN_EXPIRY_SECONDS
            ),
        }
        print(payload)
        return token_response(jwt.encode(payload, secret_key, algorithm="HS256"))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_jwt(user_id: str, orchestration_id: str, session_id: str):
    try:
        if not all([user_id, orchestration_id, session_id]):
            raise HTTPException("Missing one or more required fields for JWT payload")
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "orchestration_id": orchestration_id,
            "expires": time.time()
            + (
                ENV_PROJECT.GUEST_TOKEN_EXPIRY_DAYS
                * ENV_PROJECT.GUEST_TOKEN_EXPIRY_SECONDS
            ),
        }
        return token_response(jwt.encode(payload, secret_key, algorithm="HS256"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while generating token",
        )


def decode_jwt(token: str):
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        if "expires" in decoded_token and decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return None

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")


async def decode_email_approval_jwt(token: str):
    try:
        data = jwt.decode(token, ENV_PROJECT.EMAIL_SECRET_KEY, algorithms=["HS256"])
        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")


async def generate_approval_token(
    orchestration_id, step_id, user_id, expiration_day, SECRET_KEY
):
    payload = {
        "orchestration_id": orchestration_id,
        "step_id": step_id,
        "admin_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=expiration_day),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


async def generate_secret_key_for_admin():
    try:
        key = secrets.token_urlsafe(64)
        return key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error gnerating secret key",
        )
