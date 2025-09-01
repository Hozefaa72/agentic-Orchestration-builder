import uvicorn
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from app.database import init_db
from app.routes.auth_route import auth_router
from app.routes.thread_route import chat_router
from app.routes.message_route import router
from app.routes.assistant_route import assistant_router
from app.core.chroma_db_init import initialize_chroma
from app.middleware.middleware import TrimmedAuthMiddleware
from app.config import ENV_PROJECT
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from app.core.assistant import manager
from contextlib import asynccontextmanager

# faq= Settings().FAQ_FILE_ID
# clinic= Settings().CENTER_FILE_ID
# need = Settings().NEED_FILE_ID
# client = OpenAI(
#     api_key=Settings().OPENAI_API_KEY,
#     default_headers={"OpenAI-Beta": "assistants=v2"}
# )
# manager = IVFChatbot(client,faq,clinic,need)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await manager.initialize_assistant()
    await initialize_chroma()
    yield


app = FastAPI(
    title="Your API",
    description="API documentation for your app",
    version="1.0.0",
    openapi_tags=[{"name": "auth", "description": "Authentication endpoints"}],
    lifespan=lifespan,
    openapi_security=[{"type": "apiKey", "in": "header", "name": "Authorization"}],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
app.add_middleware(
    TrimmedAuthMiddleware, secret_key=ENV_PROJECT.SECRET_KEY, algorithm="HS256"
)
# async def startup_event():
#     await manager.initialize_assistant()
# app.add_event_handler("startup",startup_event)
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await manager.initialize_assistant()
#     await initialize_chroma({})
#     yield
# app.add_event_handler("startup", init_db)
# app.add_event_handler("shutdown", lambda: None)
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(chat_router, prefix="/thread", tags=["Thread"])
app.include_router(router, prefix="/message", tags=["Message"])
app.include_router(assistant_router, tags=["Assistant"])


# def main():
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
