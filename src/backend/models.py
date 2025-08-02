from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())
    likes_count = Column(Integer, nullable=False, server_default='0')

    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='posts')
    likes = relationship('Like', back_populates='post')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password_hash = Column(String)

    posts = relationship('Post', back_populates='owner')
    likes = relationship('Like', back_populates='user')


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    post = relationship('Post', back_populates='likes')
    user = relationship('User', back_populates='likes')

    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='_user_post_uc'),)