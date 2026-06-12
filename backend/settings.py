from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import sys
import os

IS_EXE = hasattr(sys, '_MEIPASS')

class Settings(BaseSettings):
    IS_RUN_DEV: bool = False
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

if IS_EXE:
    settings.IS_RUN_DEV = False

def get_resource_path(relative_path: str):
    """ Возвращает абсолютный путь к ресурсу, учитывая сборку PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path) # type: ignore
    return os.path.join(os.path.abspath("."), relative_path)
