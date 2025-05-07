from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from backend.app.modules.jwt_handler import decode_jwt
from typing import Optional


api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

# async def get_current_user(authorization: Optional[str] = Depends(api_key_header)):
#     print("authorization printing")
#     # If authorization header is missing, raise 401 error
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Authorization header missing")

#     try:
#         # Extract token directly as it's not in Bearer format
#         token = authorization
#     except IndexError:
#         raise HTTPException(status_code=401, detail="Invalid token format")

#     # Decode the token and verify it
#     decoded_token = decode_jwt(token)
#     if not decoded_token:
#         raise HTTPException(status_code=401, detail="Token expired or invalid")


#     return decoded_token # This will return the decoded token if it's valid
def extract_token_from_header(auth_header: str) -> str:
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    raise HTTPException(status_code=401, detail="Invalid Authorization header format")


async def get_current_user(authorization: Optional[str] = Depends(api_key_header)):
    print("authorization printing")

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = extract_token_from_header(authorization)
    decoded_token = decode_jwt(token)

    if not decoded_token:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    return decoded_token
