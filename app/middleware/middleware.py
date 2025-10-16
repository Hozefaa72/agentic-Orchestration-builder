import jwt
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

PUBLIC_ENDPOINTS = [
    "/api/auth/login",
    "/api/auth/signup",
    "/api/auth/guest_token",
    "/docs",
    "/openapi.json",
    "/api/approval/response_approval",
]


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str, algorithm: str):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm

    @staticmethod
    def extract_token(authorization: str):
        if authorization and authorization.startswith("Bearer "):
            print("Authorization header:", authorization.split(" "))
            return authorization.split(" ")[1]
        return None

    async def dispatch(self, request: Request, call_next):
        print("the request url is", request.url.path)
        if request.url.path in PUBLIC_ENDPOINTS:

            response = await call_next(request)
            return response
        if request.method == "OPTIONS":
            return await call_next(request)

        authorization: str = request.headers.get("Authorization")
        try:
            token = AuthMiddleware.extract_token(authorization)
            print("the token is", token)

            if token:
                print(f"Extracted Token: {token}")
            else:
                raise HTTPException(status_code=401, detail="Invalid or missing token.")

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")

            if user_id is None:
                raise HTTPException(
                    status_code=401, detail="Token is invalid or expired"
                )

            request.state.user_id = user_id

        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error")

        response = await call_next(request)
        return response
