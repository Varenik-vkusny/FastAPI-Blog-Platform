import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import auth, posts
from ..tg_bot.handlers import common, auth_handlers, post_handlers, registration_handlers
from ..tg_bot.core.config import settings

async def init_db():
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)



@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    await init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(registration_handlers.router)
    dp.include_router(auth_handlers.router)
    dp.include_router(post_handlers.router)
    
    asyncio.create_task(dp.start_polling(bot))

    yield

    logging.info('Приложение остановлено')


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(posts.router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_methods = ["*"],
    allow_headers = ["*"]
)