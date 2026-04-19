from functools import cache

from pydantic_settings import BaseSettings


@cache
def get_settings():
    return Settings()


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"
    DISABLE_ADMIN_AUTH_CHECK: bool = False

    DEFAULT_GSHEETS_URL: str
    DEFAULT_SEA_ROUTES_WS: str
    DEFAULT_RAIL_ROUTES_WS: str
    DEFAULT_DROPP_ROUTES_WS: str
    DEFAULT_POINTS_WS: str

    GOOGLE_SERVICE_ACCOUNT_RESOURCE_NAME: str = "google_service_account.json"
    DEFAULT_UPLOADER_FIELDS_CONFIG_RESOURCE_NAME: str = "uploader_fields_config.json"

    # JWT Configuration
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
