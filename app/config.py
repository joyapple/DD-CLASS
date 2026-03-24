from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://ddclass:iTiipYXa64BjM7bF@81.70.103.192:5432/ddclass"
    SECRET_KEY: str = "ddclass-secret-key-2024-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"

settings = Settings()
