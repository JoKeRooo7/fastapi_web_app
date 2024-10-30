from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    avatars_path: str = Field("static/avatars/", env="AVATARS_PATH")
    watermark_path: str = Field("static/watermarks/watermark.png", env="WATERMARK_PATH")
    database_url: str = Field("sqlite+aiosqlite:///database/my_database.db", env="DATABASE_URL")
    uvicorn_port: int = Field(8000, env="UVICORN_PORT")
    uvicorn_host: str = Field("0.0.0.0", env="UVICORN_HOST")

    class Config:
        env_prefix = "FAST_API_WEB_APP_"

settings = Settings()
