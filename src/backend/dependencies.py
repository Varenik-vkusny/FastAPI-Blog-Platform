from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from .database import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_post_by_owner_id(post_id: int, db: AsyncSession = Depends(get_db)) -> models.Post:

    db_post_query = select(models.Post).filter(models.Post.id == post_id)

    db_post_result = await db.execute(db_post_query)

    db_post = db_post_result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пост №{post_id} не найден!'
        )
    

    return db_post    


async def get_user_by_username(username: str, db: AsyncSession) -> models.User:

    user_db_query = select(models.User).filter(models.User.username == username)

    user_db_result = await db.execute(user_db_query)

    user_db = user_db_result.scalar_one_or_none()
    
    return user_db