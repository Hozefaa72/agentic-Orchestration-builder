from fastapi import FastAPI
from app.api_configure import configure_app
from app.database import init_db
from contextlib import asynccontextmanager
from app.routes.index import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

configure_app(app)
