from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int
    REFRESH_TOKEN_EXPIRE_SECONDS: int
    WEB_SOCKET_TIMEOUT_SECONDS: int

    @property
    def PRIVATE_KEY(self) -> str:
        with open(self.PRIVATE_KEY_PATH, 'r') as f: return f.read()

    @property
    def PUBLIC_KEY(self) -> str:
        with open(self.PUBLIC_KEY_PATH, 'r') as f: return f.read()

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra = "ignore")

settings = Settings()