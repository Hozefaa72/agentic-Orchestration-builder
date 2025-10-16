from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.config import ENV_PROJECT
from app.models.users import User
from app.models.v2.threads import Thread
from app.models.v2.message import Message
from app.models.agents_model import Agents
from app.models.knowledgebase_model import KnowledgeBase
from app.models.role_master import Role
from app.models.permission_model import Permissions
from app.models.role_permission_model import RolePermissionMapping
from app.models.llmmodels_models import LLMModel
from app.models.steps_model import Steps
from app.models.orchestration_model import Orchestration
from app.models.orchestration_instace import OrchestrationInstance
async def init_db():
    try:
        print("DataBase URL",ENV_PROJECT.DATABASE_URL)
        client = AsyncIOMotorClient(ENV_PROJECT.DATABASE_URL)
        database = client.get_database("agent_orchestration")
        await init_beanie(database, document_models=[User, Thread, Message,Agents,KnowledgeBase,Role,Permissions,RolePermissionMapping,LLMModel,Steps,Orchestration,OrchestrationInstance])
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise