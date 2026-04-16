from functools import cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
