from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    DB_URI: str
    TEST_URI: str
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_URL: str
    BASE_URL: str
    USER_PORT: int
    NOTE_PORT: int
    LABEL_PORT: int


settings = Settings()
