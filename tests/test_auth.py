import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend import models


@pytest.mark.anyio
async def test_register(client: AsyncClient, db_session: AsyncSession):

    json = {
        'username': 'new_user',
        'password': 'new_password'
    }

    response = await client.post('/register', json=json)

    assert response.status_code == 201

    data = response.json()

    user_db = await db_session.get(models.User, data['id'])

    assert user_db 
    assert 'id' in data
    assert data['username'] == 'new_user'
    assert 'password' not in data



@pytest.mark.anyio
async def test_duplicate_user(client: AsyncClient, test_user: models.User):

    json = {
        'username': test_user.username,
        'password': 'some_words'
    }

    response = await client.post('/register', json=json)

    assert response.status_code == 400
    assert response.json()['detail'] == 'Пользователь с таким ником уже есть!'



@pytest.mark.anyio
async def test_authenticate_user(client: AsyncClient, test_user: models.User):

    data = {
        'username': test_user.username,
        'password': 'testpassword'
    }

    response = await client.post('/token', data=data)

    assert response.status_code == 200

    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'



@pytest.mark.anyio
async def test_not_seuccessful_username(client: AsyncClient):
    
    data = {
        'username': 'some_user',
        'password': 'something'
    }

    response = await client.post('/token', data=data)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Неправильный ник или пароль'



@pytest.mark.anyio
async def test_not_successful_password(client: AsyncClient, test_user: models.User):

    data = {
        'username': test_user.username,
        'password': 'something'
    }

    response = await client.post('/token', data=data)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Неправильный ник или пароль'

