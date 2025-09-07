from typing import Annotated
from fastapi import Depends
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///convergent.db"
    client_origin: str = "http://localhost:5173"
    secret_key: str
    algorithm: str = "HS256"
    expires_delta_seconds: int = 3600

    class Config:
        env_file = ".env"


settings = Settings()


def get_settings() -> Settings:
    return settings


SettingsDep = Annotated[Settings, Depends(get_settings)]
