from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt
from .config import get_settings

settings = get_settings()


ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
TOKEN_ACCESS_EXPIRE_MINUTES = settings.token_access_expire_minutes

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hash_password: str) -> bool:
    return pwd_context.verify(plain_password, hash_password)


def create_access_token(data: dict, expire_minutes: Optional[timedelta] = None):

    to_encode = data.copy()

    if expire_minutes:
        expire = datetime.now(timezone.utc) + expire_minutes
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_ACCESS_EXPIRE_MINUTES)

    to_encode['exp'] = expire

    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt