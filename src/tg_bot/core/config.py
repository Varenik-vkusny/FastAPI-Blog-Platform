from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_base_url: str
    bot_token: str

    class Config():
        env_file = '.env'
        extra = 'ignore'

settings = Settings()