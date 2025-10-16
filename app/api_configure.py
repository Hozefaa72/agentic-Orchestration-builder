from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.events import create_start_app_handler
from app.routes.index import router
from app.utils.config import ENV_PROJECT
from app.middleware.middleware import AuthMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.scheduler_core import check_step_timeouts

scheduler = AsyncIOScheduler()

def configure_app(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        AuthMiddleware, secret_key=ENV_PROJECT.SECRET_KEY, algorithm="HS256"
    )
    app.include_router(router, prefix="/api")

def configure_database(app: FastAPI):
    app.add_event_handler("startup", create_start_app_handler(app))


def configure_scheduler(app: FastAPI):
    scheduler.add_job(check_step_timeouts, "interval", days=1)
    app.add_event_handler("startup", scheduler.start)
    app.add_event_handler("shutdown", scheduler.shutdown)