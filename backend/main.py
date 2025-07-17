from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, SessionLocal
from .routers import auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/posts', response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user = Depends(auth.get_current_user)):

    new_post = models.Post(**post.dict(), owner_id = current_user.id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@app.get('/posts', response_model=list[schemas.Post], status_code=status.HTTP_200_OK)
async def get_posts(step: int=0, limit: int=100, db: Session = Depends(get_db)):

    posts = db.query(models.Post).offset(step).limit(limit).all()

    return posts