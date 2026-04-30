from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DATABASE
    DB_SCHEME: str
    DB_HOST: str
    DB_PORT: int = 3306

    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    DB_CHARSET: str = "utf8mb4"
    DB_COLLATE: str = "utf8mb4_unicode_ci"

    # AUTH
    admin_login: str
    admin_password: str
    jwt_algorithm: str
    authjwt_secret_key: str
    access_token_expire_minutes: int
    # Configure application to store and get JWT from cookies.
    authjwt_token_location: set = {"cookies"}
    # HTTPS only?
    authjwt_cookie_secure: bool = False
    # CSRF double submit protection.
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_samesite: str = "lax"


@cache
def get_settings():
    return Settings()
