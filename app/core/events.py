from fastapi import FastAPI
from loguru import logger
from typing import Callable
from app.database import init_db

listen_task = None


def create_start_app_handler(app: FastAPI) -> Callable:

    @logger.catch
    async def start_app() -> None:
        try:
            await init_db()
        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise e

    return start_app
