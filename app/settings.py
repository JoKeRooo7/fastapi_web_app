from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field("AS-d321.dsaD_-21CS-d3", env="SK")
    ENCRYPTION: str = Field("HS256", env="ENCRYPTION")
    AVATARS_PATH: str = Field("static/avatars/", env="AVATARS_PATH")
    UVICORN_PORT: int = Field(8000, env="UVICORN_PORT")
    UVICORN_HOST: str = Field("0.0.0.0", env="UVICORN_HOST")
    REDIS_PATH: str = Field("database", env="REDIS_PATH")
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    DAILY_RATING_LIMIT: int = Field(5, env="DAILY_RATING_LIMIT")
    TIME_TO_REMOVE_LIMIT: int = Field(3, env="TIME_TO_REMOVE_LIMIT")
    TIME_TO_REMOVE_LIST_CASH: int = Field(3600, env="TIME_TO_REMOVE_LIST_CASH")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    WATERMARK_PATH: str = Field(
        "static/watermarks/watermark.png", env="WATERMARK_PATH")
    DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///database/my_database.db", env="DATABASE_URL")

    class Config:
        env_prefix = "FAST_API_WEB_APP_"


settings = Settings()
