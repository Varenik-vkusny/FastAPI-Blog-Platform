from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class UserCreate(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: int
    username: str

    class Config():
        from_attributes=True


class Post(PostBase):
    id: int
    created_at: datetime
    owner: User
    likes_count: int=0

    class Config():
        from_attributes=True


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config():
        from_attributes=True


class TokenData(BaseModel):
    username: Optional[str] = None