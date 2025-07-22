from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from backend.app.config import settings
from backend.app.models.users import User
from backend.app.models.threads import Thread
from backend.app.models.message import Message
async def init_db():
    try:
        print("DataBase URL",settings.DATABASE_URL)
        client = AsyncIOMotorClient(settings.DATABASE_URL)
        database = client.get_database("indra_ivf")
        # Initialize Beanie with the database and models
        await init_beanie(database, document_models=[User, Thread, Message])
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise