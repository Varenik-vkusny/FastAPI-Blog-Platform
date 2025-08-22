import redis.asyncio as redis
import json
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import TypeAdapter
from . import models, schemas
from .database import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_user_by_username(username: str, db: AsyncSession) -> models.User:

    user_db_query = select(models.User).filter(models.User.username == username)

    user_db_result = await db.execute(user_db_query)

    user_db = user_db_result.scalar_one_or_none()
    
    return user_db


async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)) -> models.Post:

    db_post_query = select(models.Post).filter(models.Post.id == post_id)

    db_post_result = await db.execute(db_post_query)

    db_post = db_post_result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пост №{post_id} не найден!'
        )
    
    return db_post


async def get_posts_by_user_id(user_id:int, redis_client: redis.Redis, db: AsyncSession) -> list[schemas.Post]:

    cache_key = str(user_id)

    cache_posts = await redis_client.get(cache_key)

    if cache_posts:
        print('CACHE HIT')

        cache_posts_adapter = TypeAdapter(list[schemas.Post])

        return cache_posts_adapter.validate_json(cache_posts)
    
    print('CACHE MISS')

    db_result = await db.execute(select(models.Post).where(models.Post.owner_id == user_id))

    db_posts = db_result.scalars().all()

    pydantic_posts = [schemas.Post.model_validate(post) for post in db_posts]

    await redis_client.set(cache_key, json.dumps(jsonable_encoder(pydantic_posts)), ex=600)

    return pydantic_posts