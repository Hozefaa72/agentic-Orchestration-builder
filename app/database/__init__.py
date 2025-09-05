from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import ENV_PROJECT
from app.models.users import User
from app.models.threads import Thread
from app.models.message import Message
from app.models.user_info import User_Info
async def init_db():
    try:
        # print("DataBase URL",ENV_PROJECT.DATABASE_URL)
        print("initialzing database")
        client = AsyncIOMotorClient(ENV_PROJECT.DATABASE_URL)
        database = client.get_database("indra_ivf")
        # Initialize Beanie with the database and models
        await init_beanie(database, document_models=[User, Thread, Message,User_Info])
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise