from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from .. import models, schemas, security
from ..database import get_db

router = APIRouter(
    tags=['Authorization']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router.post('/register', response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):

    user_db_query = select(models.User).filter(models.User.username == user.username)

    user_db_result = await db.execute(user_db_query)

    user_db = user_db_result.scalar_one_or_none()

    if user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким ником уже есть!"
        )
    
    password_hash = security.hash_password(user.password)
    
    user_db = models.User(username=user.username, password_hash=password_hash)

    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)

    return user_db



@router.post('/token', response_model=schemas.Token, status_code=status.HTTP_200_OK)
async def login(user: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    db_user_query = select(models.User).filter(models.User.username == user.username)

    db_user_result = await db.execute(db_user_query)

    db_user = db_user_result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильный ник или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        
    
    if not security.verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильный ник или пароль',
            headers={'WWW-Authenticate': 'Bearer'}
        )
        
    
    user_data = {'sub': db_user.username}

    access_token = security.create_access_token(data=user_data)
    
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Вы не авторизованы!',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try: 
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])

        username: str = payload.get('sub')

        if not username:
            raise credential_exception
        
        tokenData = schemas.TokenData(username=username)
    except JWTError:
        raise credential_exception
    

    db_user_query = select(models.User).filter(models.User.username == tokenData.username)

    db_user_result = await db.execute(db_user_query)

    db_user = db_user_result.scalar_one_or_none()

    if not db_user:
        raise credential_exception
    
    return db_user