import logging
import redis.asyncio as redis
from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from .routers import auth, posts
from . import clients
from .config import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logging.info("Приложение запускается")

    logging.info("Инициализирую redis_client")

    clients.redis_client = redis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )

    yield

    logging.info("Приложение остановлено")


app = FastAPI(lifespan=lifespan)
instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

app.include_router(auth.router)
app.include_router(posts.router)
