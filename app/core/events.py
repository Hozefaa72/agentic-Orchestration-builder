from beanie import init_beanie
from fastapi import FastAPI
from loguru import logger
from app.utils.config import ENV_PROJECT
from app.database import mongodb
# from app.modules.async_redis_consumer import aredis, start_redis_consumer
import asyncio
from typing import Callable

from app.models.threads import Thread
from app.models.message import Message
from app.models.users import User
from app.models.user_info import User_Info

listen_task = None

def create_start_app_handler(app: FastAPI) -> Callable:

    @logger.catch
    async def start_app() -> None:
        try:
            await mongodb.client.admin.command("ping")
            logger.info("MongoDB Connected.")

            # ✅ Get the DB name safely
            db_name = getattr(ENV_PROJECT, "MONGO_DB_NAME", "IVF_CHATBOT") or "IVF_CHATBOT"
            logger.info(f"Using DB: {db_name}")

            # ✅ Initialize Beanie
            await init_beanie(
                database=mongodb.client[db_name],
                document_models=[Thread, Message, User, User_Info],
            )

            # await start_redis()
            # logger.info("Redis Connected.")

        except Exception as e:
            logger.error(f"Startup error: {e}")
            raise e

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:

    @logger.catch
    async def stop_app() -> None:
        try:
            mongodb.client.close()
            logger.info("Closed MongoDB Connection")

            # await stop_redis()
            # logger.info("Closed Redis Connection")

        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            raise e

    return stop_app


# async def start_redis():
#     global listen_task
#     try:
#         if await aredis.client.ping():
#             listen_task = asyncio.create_task(start_redis_consumer("run_chat"))
#     except Exception as e:
#         logger.error(f"Redis start error: {e}")
#         raise e


# async def stop_redis():
#     global listen_task
#     try:
#         await aredis.pubsub.close()
#         await aredis.close()
#         logger.info("Redis connection closed.")
#     except Exception as e:
#         logger.error(f"Redis stop error: {e}")
#         raise e
#     finally:
#         logger.info("Background PubSub Listener stopped.")
#         if listen_task:
#             listen_task.cancel()
