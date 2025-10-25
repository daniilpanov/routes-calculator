import os

from pydantic import BaseModel


class Settings(BaseModel):
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


settings = Settings(
    jwt_algorithm=os.environ["JWT_ALGORITHM"],
    authjwt_secret_key=os.environ["AUTHJWT_SECRET_KEY"],
    access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 0)),
)
