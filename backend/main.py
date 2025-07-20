from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, posts
import pydantic
import sys
print(f"!!! PYDANTIC VERSION BEING USED: {pydantic.__version__} !!!")

# Эта строчка покажет, какой именно файл Python.exe запускает твой код
print(f"!!! PYTHON EXECUTABLE BEING USED: {sys.executable} !!!")

async def init_db():
    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all())

app = FastAPI()
app.include_router(auth.router)
app.include_router(posts.router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_methods = ["*"],
    allow_headers = ["*"]
)