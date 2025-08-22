from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    algorithm: str
    secret_key: str
    token_access_expire_minutes: int
    bot_token: str
    redis_url: str

    model_config = SettingsConfigDict(env_file = '.env', extra = 'ignore')


@lru_cache
def get_settings():
    return Settings()

def get_test_settings():
    return Settings(
        sqlalchemy_database_url="sqlite+aiosqlite:///:memory:",
        redis_url=f"redis://localhost:6381/1",
        algorithm="HS256",
        secret_key="test_secret_key_for_jwt_tokens",
        token_access_expire_minutes=30,
        bot_token="fake_bot_token"
    )