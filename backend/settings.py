from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    IS_RUN_DEV: bool = False
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
