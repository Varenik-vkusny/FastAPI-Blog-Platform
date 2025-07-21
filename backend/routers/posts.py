from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from .. import models, schemas
from ..database import get_db
from . import auth

router = APIRouter()

@router.post('/posts', response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.PostCreate, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_current_user)):

    new_post = models.Post(**post.dict(), owner_id = current_user.id)

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return new_post


@router.get('/posts', response_model=list[schemas.Post], status_code=status.HTTP_200_OK)
async def get_posts(step: int=0, limit: int=100, db: AsyncSession = Depends(get_db)):

    results_start = select(models.Post).options(joinedload(models.Post.owner)).order_by(models.Post.created_at.desc()).offset(step).limit(limit)
    

    results_data = await db.execute(results_start)

    posts = results_data.scalars().all()

    return posts


@router.put('/post/{post_id}', response_model=schemas.Post, status_code=status.HTTP_200_OK)
async def update_post(post_id: int, update_post: schemas.PostBase, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_current_user)):

    post_query = select(models.Post).filter(models.Post.id == post_id)
    db_post_result = await db.execute(post_query)

    db_post = db_post_result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пост №{post_id} не найден!'
        )
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для редактирования поста.'
        )
    
    
    post_update = update_post.model_dump(exclude_unset=True)

    for key, value in post_update.items():
        setattr(db_post, key, value)

    await db.commit()

    await db.refresh(db_post)

    return db_post



@router.delete('/post/{post_id}', status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_current_user)):

    db_post_query = select(models.Post).filter(models.Post.id == post_id)

    db_post_result = await db.execute(db_post_query)

    db_post = db_post_result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пост №{post_id} не найден!'
        )
    
    if current_user.id != db_post.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='У вас недостаточно прав на удаление этого поста!'
        )
    
    await db.delete(db_post)

    await db.commit()

    return {'detail': f'Пост №{post_id} успешно удален!'}


@router.post('/post/{post_id}/like')
async def like(post_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_current_user)):
    
    

    post_db = await db.get(models.Post, post_id)

    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет поста"
        )

    existing_like_query = select(models.Like).filter(models.Like.post_id == post_id, models.Like.user_id == current_user.id)

    existing_like_result = await db.execute(existing_like_query)

    existing_like = existing_like_result.scalar_one_or_none()

    if not existing_like:
        new_like = models.Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        post_db.likes_count += 1
        await db.commit()
        return {'detail': 'Лайк поставлен'}
    else:
        await db.delete(existing_like)
        post_db.likes_count -= 1
        await db.commit()
        return {'detail': 'Лайк убран'}