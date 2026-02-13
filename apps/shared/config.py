from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_SCHEME: str
    DB_HOST: str
    DB_PORT: int = 3306

    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    DB_CHARSET: str = "utf8mb4"
    DB_COLLATE: str = "utf8mb4_unicode_ci"


@cache
def get_settings():
    return Settings()
