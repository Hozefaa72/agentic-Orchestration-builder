from fastapi import APIRouter
from app.routes import auth_route, thread_route, message_route, assistant_route

# The main router for the application
router = APIRouter()

# Include individual routers with their respective prefixes and tags
router.include_router(auth_route.router, prefix="/auth", tags=["Authentication"])
router.include_router(thread_route.router, prefix="/thread", tags=["Thread"])
router.include_router(message_route.router, prefix="/message", tags=["Message"])
router.include_router(assistant_route.router, prefix="/assistant", tags=["Assistant"])
