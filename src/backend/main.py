import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import auth, posts
from ..tg_bot.core.config import settings

async def init_db():
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logging.info('Приложение запускается')

    await init_db()

    yield

    logging.info('Приложение остановлено')


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(posts.router)