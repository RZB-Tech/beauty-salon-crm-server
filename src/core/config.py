from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"]

    DATABASE_URL: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    REFRESH_TOKEN_EXPIRE_SECONDS: int
    REDIS_BROKER: str
    REDIS_BACKEND: str

    ADMIN_PRIVATE_KEY_PATH: str
    ADMIN_PUBLIC_KEY_PATH: str
    ADMIN_ALGORITHM: str
    ADMIN_ACCESS_TOKEN_EXPIRE_SECONDS: int
    SQLADMIN_SESSION_SECRET: str

    LOGIN_MAX_FAILED_ATTEMPTS: int = 10
    ATTEMPTS_WINDOW_TTL: int = 600 # in seconds
    LOGIN_BLOCK_TTL: int = 3600 # in seconds
    IP_BLOCK_TTL: int = 86400 # in seconds

    # SQLAdmin login - counted separately from the staff login above
    ADMIN_LOGIN_MAX_FAILED_ATTEMPTS: int = 3   # per login, from any IP
    ADMIN_IP_MAX_FAILED_ATTEMPTS: int = 10     # per IP, across all logins
    ADMIN_ATTEMPTS_WINDOW_TTL: int = 900 # in seconds
    ADMIN_LOGIN_BLOCK_TTL: int = 3600 # in seconds
    ADMIN_IP_BLOCK_TTL: int = 86400 # in seconds

    ERROR_ALERTS_BOT_TOKEN: str | None = None
    ERROR_ALERTS_CHAT_ID: str | None = None

    CLICK_SERVICE_ID: int
    CLICK_MERCHANT_ID: int
    CLICK_MERCHANT_USER_ID: int
    CLICK_SECRET_KEY: str
    CLICK_RETURN_URL: str

    CLICK_API_BASE_URL: str = "https://api.click.uz/v2/merchant"
    CLICK_CHECKOUT_URL: str = "https://my.click.uz/services/pay"
    # Telegram mini app (our platform bot, not tenants' own bots from TenantIntegration)
    TELEGRAM_MINIAPP_BOT_TOKEN: str | None = None
    TELEGRAM_MINIAPP_ORIGIN: str | None = None # added to CORS allowed origins in production
    TELEGRAM_INIT_DATA_EXPIRE_SECONDS: int = 86400
    MINIAPP_MAX_PENDING_REQUESTS_PER_TENANT: int = 3

    @property
    def PRIVATE_KEY(self) -> str:
        with open(self.PRIVATE_KEY_PATH, 'r') as f: return f.read()

    @property
    def PUBLIC_KEY(self) -> str:
        with open(self.PUBLIC_KEY_PATH, 'r') as f: return f.read()

    @property
    def ADMIN_PRIVATE_KEY(self) -> str:
        with open(self.ADMIN_PRIVATE_KEY_PATH, 'r') as f: return f.read()

    @property
    def ADMIN_PUBLIC_KEY(self) -> str:
        with open(self.ADMIN_PUBLIC_KEY_PATH, 'r') as f: return f.read()

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra = "ignore")

settings = Settings()