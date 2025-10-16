from fastapi import APIRouter
from app.routes import auth_route, agents_route,role_master_route,permission_route,llmmodel_route,knowledge_base_route,rolepermissionmapping_route,steps_route,orchestration_route,approval_route
from app.routes.v2 import assistant_route, message_route, thread_route

# The main router for the application
router = APIRouter()

# Include individual routers with their respective prefixes and tags
router.include_router(auth_route.router, prefix="/auth", tags=["Authentication"])
router.include_router(thread_route.router, prefix="/thread", tags=["Thread"])
router.include_router(message_route.router, prefix="/message", tags=["Message"])
router.include_router(assistant_route.router, prefix="/assistant", tags=["Assistant"])
router.include_router(agents_route.router, prefix="/agent", tags=["Agent"])
router.include_router(role_master_route.router, prefix="/role", tags=["Role Master"])
router.include_router(permission_route.router, prefix="/permission", tags=["Permission"])
router.include_router(llmmodel_route.router, prefix="/llmmodel", tags=["LLM Model"])
router.include_router(knowledge_base_route.router, prefix="/knowledgebase", tags=["Knowledge Base"])
router.include_router(rolepermissionmapping_route.router, prefix="/rolepermissionmapping", tags=["Role Permission Mapping"])
router.include_router(steps_route.router, prefix="/steps", tags=["Steps"])
router.include_router(orchestration_route.router, prefix="/orchestration", tags=["Orchestration"])
router.include_router(approval_route.router, prefix="/approval", tags=["Approval"])
