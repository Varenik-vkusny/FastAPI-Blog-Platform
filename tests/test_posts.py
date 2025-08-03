import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend import models


@pytest.mark.anyio
async def test_create_post(authenticated_client: AsyncClient, test_user: models.User):

    json = {
        'title': 'Новый пост',
        'content': 'Новый текст'
    }

    response = await authenticated_client.post('/posts', json=json)

    assert response.status_code == 201
    data = response.json()

    assert 'id' in data
    assert 'created_at' in data
    assert data['owner']['username'] == test_user.username
    assert 'likes_count' in data
    assert data['title'] == 'Новый пост'
    assert data['content'] == 'Новый текст'



@pytest.mark.anyio
async def test_not_authenticated_user_create(client: AsyncClient):

    json = {
        'title': 'Что то',
        'content': 'Еще что то'
    }

    response = await client.post('/posts', json=json)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'



@pytest.mark.anyio
async def test_get_posts(client: AsyncClient, test_user: models.User, db_session: AsyncSession):

    # ПРЕДУСЛОВИЕ

    post1 = models.Post(title='Пост', content='Текст', owner_id=test_user.id)
    post2 = models.Post(title='Новый', content='Новый текст', owner_id=test_user.id)

    db_session.add_all([post1, post2])
    await db_session.commit()

    response = await client.get('/posts')

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)

    assert len(data) == 2



@pytest.mark.anyio
async def test_put_post(authenticated_client: AsyncClient, test_user: models.User, db_session: AsyncSession):

    post = models.Post(title='Новый пост', content='Новый текст', owner_id=test_user.id)
    
    db_session.add(post)
    await db_session.commit()


    json = {
        'title': 'Титл для put',
        'content': 'Текст для put'
    }

    response = await authenticated_client.put(f'/post/{post.id}', json=json)

    assert response.status_code == 200

    data = response.json()
    assert data['id'] == post.id
    assert data['title'] == 'Титл для put'
    assert data['content'] == 'Текст для put'
    assert data['owner']['username'] == test_user.username



@pytest.mark.anyio
async def test_not_authenticated_put(client: AsyncClient):

    json = {
        'title': 'not auth title',
        'content': 'not auth content'
    }

    response = await client.put('/post/1', json=json)

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'



@pytest.mark.anyio
async def test_no_post_id_put(authenticated_client: AsyncClient):

    json = {
        'title': 'some title',
        'content': 'some text'
    }

    response = await authenticated_client.put(f'/post/{32}', json=json)

    assert response.status_code == 404
    assert response.json()['detail'] == f'Пост №32 не найден!'



@pytest.mark.anyio
async def test_not_current_user_put(client: AsyncClient, test_user: models.User, db_session: AsyncSession):

    # ПРЕДУСЛОВИЕ

    from src.backend.security import hash_password

    user = models.User(username='user', password_hash=hash_password('userpassword'))

    db_session.add(user)
    await db_session.commit()


    data = {
        'username': 'user',
        'password': 'userpassword'
    }

    response = await client.post('/token', data=data)

    token_data = response.json()

    access_token = token_data['access_token']

    client.headers['Authorization'] = f'Bearer {access_token}'

    post = models.Post(title='Новый пост', content='Новый текст', owner_id=test_user.id)
    
    db_session.add(post)
    await db_session.commit()


    json = {
        'title': 'usertitle',
        'content': 'usercontent'
    }

    response = await client.put(f'/post/{post.id}', json=json)

    assert response.status_code == 403
    assert response.json()['detail'] == 'Недостаточно прав для редактирования поста.'



@pytest.mark.anyio
async def test_delete_post(authenticated_client: AsyncClient, test_user: models.User, db_session: AsyncSession):

    post = models.Post(title='Новый пост', content='Новый текст', owner_id=test_user.id)
    
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)

    post_id = post.id

    response = await authenticated_client.delete(f'/post/{post_id}')

    
    assert response.status_code == 200

    db_session.expire_all()   

    db_post = await db_session.get(models.Post, post_id)
    assert db_post is None
    assert response.json()['detail'] == f'Пост №{post_id} успешно удален!'



@pytest.mark.anyio
async def test_not_authenticated_delete(client: AsyncClient):

    response = await client.delete('/post/1')

    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'



@pytest.mark.anyio
async def test_no_post_id_delete(authenticated_client: AsyncClient):

    response = await authenticated_client.delete('/post/32')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Пост №32 не найден!'



@pytest.mark.anyio
async def test_not_current_user_delete(client: AsyncClient, test_user: models.User, db_session: AsyncSession):
    
    # ПРЕДУСЛОВИЕ

    post = models.Post(title='Новый пост', content='Новый текст', owner_id=test_user.id)
    
    db_session.add(post)
    await db_session.commit()


    from src.backend.security import hash_password

    user = models.User(username='user2', password_hash=hash_password('userpassword2'))

    db_session.add(user)
    await db_session.commit()


    data = {
        'username': 'user2',
        'password': 'userpassword2'
    }

    response = await client.post('/token', data=data)

    token_data = response.json()

    access_token = token_data['access_token']

    client.headers['Authorization'] = f'Bearer {access_token}'


    response = await client.delete(f'/post/{post.id}')

    assert response.status_code == 403
    assert response.json()['detail'] == 'У вас недостаточно прав на удаление этого поста!'



@pytest.mark.anyio
async def test_like_post(authenticated_client: AsyncClient, db_session: AsyncSession, test_user: models.User):

    post = models.Post(title='Новый пост', content='Новый текст', owner_id=test_user.id)
    
    db_session.add(post)
    await db_session.commit()

    response = await authenticated_client.post(f'/post/{post.id}/like')

    assert response.status_code == 200
    assert response.json()['detail'] == 'Лайк поставлен'