# from app.utils.config import ENV_PROJECT
# from app.database.connections.mongo import MongoDB
# from app.database.utils.tunnel_and_secret import build_documentdb_uri

# # Step 1: Build the DocumentDB URI after setting up SSH + fetching credentials
# final_mongo_uri = build_documentdb_uri()

# mongodb: MongoDB = MongoDB()
# # mongodb.init_connection(ENV_PROJECT.MONGO_URI)
# mongodb.init_connection(final_mongo_uri)


# class Clients:
#     mongodb = mongodb.client
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import ENV_PROJECT
from app.models.users import User
from app.models.threads import Thread
from app.models.message import Message
from app.models.user_info import User_Info
async def init_db():
    try:
        print("DataBase URL",ENV_PROJECT.DATABASE_URL)
        client = AsyncIOMotorClient(ENV_PROJECT.DATABASE_URL)
        database = client.get_database("indra_ivf")
        # Initialize Beanie with the database and models
        await init_beanie(database, document_models=[User, Thread, Message,User_Info])
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise