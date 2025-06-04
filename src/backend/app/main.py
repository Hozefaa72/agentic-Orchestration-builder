import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from backend.app.database import init_db
from backend.app.routes.auth_route import auth_router
from backend.app.routes.thread_route import chat_router
from backend.app.routes.message_route import router
from backend.app.routes.assistant_route import assistant_router
from backend.app.utils.middleware import TrimmedAuthMiddleware
from backend.app.config.config import Settings
from fastapi.middleware.cors import CORSMiddleware

setting = Settings()
app = FastAPI(
    title="Your API",
    description="API documentation for your app",
    version="1.0.0",
    openapi_tags=[{"name": "auth", "description": "Authentication endpoints"}],
    openapi_security=[{"type": "apiKey", "in": "header", "name": "Authorization"}],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
app.add_middleware(
    TrimmedAuthMiddleware, secret_key=setting.SECRET_KEY, algorithm="HS256"
)
app.add_event_handler("startup", init_db)
app.add_event_handler("shutdown", lambda: None)
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/thread", tags=["Thread"])
app.include_router(router, prefix="/message", tags=["Message"])
app.include_router(assistant_router, tags=["Assistant"])


def main():
     uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8001, reload=True)

