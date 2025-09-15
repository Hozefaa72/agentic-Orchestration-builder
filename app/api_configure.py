from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.routes.index import router
from app.utils.config import ENV_PROJECT
from app.middleware.middleware import TrimmedAuthMiddleware


def configure_app(app: FastAPI):
    """
    Configures the FastAPI application with middleware and routers.
    """
    # Add CORS middleware using settings from the config file
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
    app.add_middleware(
        TrimmedAuthMiddleware, secret_key=ENV_PROJECT.SECRET_KEY, algorithm="HS256"
    )

    app.include_router(router, prefix="/api")

def configure_database(app: FastAPI):
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))