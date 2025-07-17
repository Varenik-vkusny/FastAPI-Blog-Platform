from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())

    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='posts')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password_hash = Column(String)

    posts = relationship('Post', back_populates='owner')