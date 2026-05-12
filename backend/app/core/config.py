from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://poc_user:poc_password@localhost:5432/poc_ictim"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    NLP_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    UPLOAD_DIR: str = "/app/uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
