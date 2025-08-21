import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator
from src.backend.database import Base
from src.backend.dependencies import get_db
from src.backend.main import app
from src.backend import models

TEST_DATABASE = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(TEST_DATABASE)

TestAsyncLocalSession = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(autouse=True, scope='function')
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def client() -> AsyncGenerator[AsyncClient, None]:

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestAsyncLocalSession() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncLocalSession() as session:
        yield session


@pytest.fixture(scope='function')
async def test_user(db_session: AsyncSession) -> models.User:

    from src.backend.security import hash_password

    user = models.User(username='testuser', password_hash=hash_password('testpassword'))

    db_session.add(user)
    await db_session.commit()

    return user


@pytest.fixture(scope='function')
async def authenticated_client(client: AsyncClient, test_user: models.User) -> AsyncClient:

    data = {
        'username': test_user.username,
        'password': 'testpassword'
    }

    response = await client.post('/token', data=data)

    token_data = response.json()

    access_token = token_data['access_token']

    client.headers['Authorization'] = f'Bearer {access_token}'


    return client