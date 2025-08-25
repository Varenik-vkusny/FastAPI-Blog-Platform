import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import TypeAdapter
from src.backend import schemas, models
from src.backend.dependencies import get_posts_by_user_id


@pytest.mark.anyio
async def test_redis_cache_hit():

    test_redis = AsyncMock()
    test_db = AsyncMock()

    fake_data = [
        schemas.Post(
            id=55,
            title='Redis_title',
            content='Redis_content',
            owner=schemas.User(
                id=55,
                username='test_redis'
            )
        )
    ]

    cache_posts_adapter = TypeAdapter(list[schemas.Post])

    test_redis.get.return_value = cache_posts_adapter.dump_json(fake_data)

    result = await get_posts_by_user_id(user_id=55, redis_client=test_redis, db=test_db)

    test_redis.get.assert_awaited_once_with(str(55))
    test_db.execute.assert_not_called()

    assert result == fake_data



@pytest.mark.anyio
async def test_redis_cache_miss():

    from src.backend.security import hash_password

    test_redis = AsyncMock()
    test_db = AsyncMock()

    fake_data = [
        models.Post(
            id=56,
            title='Test',
            content='Miss',
            owner_id=56,
            owner=models.User(
                id=56,
                username='test_miss',
                password_hash=hash_password('pass_miss')
            ),
            likes_count=0
        )
    ]

    mock_scalar = MagicMock()
    mock_scalar.scalars.return_value.all.return_value = fake_data

    test_db.execute.return_value = mock_scalar

    test_redis.get.return_value = None

    result = await get_posts_by_user_id(user_id=56, redis_client=test_redis, db=test_db)

    test_redis.get.assert_awaited_once()
    test_db.execute.assert_awaited_once()

    assert result == [schemas.Post.model_validate(data) for data in fake_data]