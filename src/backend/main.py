import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers import auth, posts

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logging.info('Приложение запускается')

    yield

    logging.info('Приложение остановлено')


app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(posts.router)