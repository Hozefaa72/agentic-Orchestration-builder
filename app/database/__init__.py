from app.config import ENV_PROJECT
from app.database.connections.mongo import MongoDB
from app.database.utils.tunnel_and_secret import build_documentdb_uri

# Step 1: Build the DocumentDB URI after setting up SSH + fetching credentials
final_mongo_uri = build_documentdb_uri()

mongodb: MongoDB = MongoDB()
# mongodb.init_connection(ENV_PROJECT.MONGO_URI)
mongodb.init_connection(final_mongo_uri)


class Clients:
    mongodb = mongodb.client
