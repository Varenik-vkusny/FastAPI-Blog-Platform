from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
from . import auth

router = APIRouter()

@router.post('/posts', response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):

    new_post = models.Post(**post.dict(), owner_id = current_user.id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get('/posts', response_model=list[schemas.Post], status_code=status.HTTP_200_OK)
async def get_posts(step: int=0, limit: int=100, db: Session = Depends(get_db)):

    results = (
        db.query(
            models.Post,
            func.count(models.Like.id).label('likes_count')
        )
        .outerjoin(models.Like, models.Post.id == models.Like.post_id)
        .group_by(models.Post.id)
        .order_by(models.Post.created_at.desc())
        .offset(step)
        .limit(limit)
        .all()
    )

    posts_with_likes = []
    for post, likes_count in results:
        post_schema = schemas.Post.from_orm(post)
        post_schema.likes_count = likes_count
        posts_with_likes.append(post_schema)

    return posts_with_likes


@router.put('/posts/{post_id}', response_model=schemas.Post, status_code=status.HTTP_200_OK)
async def update_post(post_id: int, update_post: schemas.PostBase, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    db_post = post_query.first()

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
    
    post_query.update(update_post.dict(), synchronize_session=False)

    db.commit()

    return db_post


@router.post('/post/{post_id}/like')
async def like(post_id: int, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):
    
    post_db = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет поста"
        )
    
    existing_like = db.query(models.Like).filter(models.Like.post_id == post_id, models.Like.user_id == current_user.id).first()

    if not existing_like:
        new_like = models.Like(post_id=post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return {'detail': 'Лайк поставлен'}
    else:
        db.delete(existing_like)
        db.commit()
        return {'detail': 'Лайк убран'}