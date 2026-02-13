from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    FESCO_API_KEY: str


@cache
def get_settings():
    return Settings()
