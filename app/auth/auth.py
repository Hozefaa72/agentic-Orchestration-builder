from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from app.auth.jwt_handler import decode_jwt
from typing import Optional

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def extract_token_from_header(auth_header: str) -> str:
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    raise HTTPException(status_code=401, detail="Invalid Authorization header format")


async def get_current_user(authorization: Optional[str] = Depends(api_key_header)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = await extract_token_from_header(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or malformed token in header",
            )
        decoded_token = decode_jwt(token)

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Token expired or invalid")

        return decoded_token

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )
