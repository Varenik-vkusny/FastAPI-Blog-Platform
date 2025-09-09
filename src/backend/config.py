from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from functools import lru_cache


class Settings(BaseSettings):
    db_driver: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    redis_host: str
    redis_port: int
    redis_db: int

    algorithm: str
    secret_key: str
    token_access_expire_minutes: int
    bot_token: str

    @computed_field
    @property
    def sqlalchemy_database_url(self) -> str:
        if self.db_driver.startswith("sqlite"):
            return f"{self.db_driver}:///{self.db_name}"

        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings():
    return Settings()


def get_test_settings():
    return Settings(
        redis_host="localhost",
        redis_db=1,
        redis_port=6381,
        algorithm="HS256",
        secret_key="test_secret_key_for_jwt_tokens",
        token_access_expire_minutes=30,
        bot_token="fake_bot_token",
    )
