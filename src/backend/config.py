from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    sqlalchemy_database_url: str
    algorithm: str
    secret_key: str
    token_access_expire_minutes: int

    model_config = SettingsConfigDict(env_file = '.env', extra = 'ignore')


settings = Settings()