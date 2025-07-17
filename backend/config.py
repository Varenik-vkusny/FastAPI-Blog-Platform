from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    algorithm: str
    secret_key: str
    token_access_expire_minutes: int

    class Config():
        env_file = '../.env'


settings = Settings()