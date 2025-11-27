from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., gt=0)
    DATABASE_URL: str = Field(..., min_length=10)
    ALGORITHM: str = Field(..., min_length=3)
    uvicorn_host: str = Field(..., alias="UVICORN_HOST")
    uvicorn_port: int = Field(..., alias="UVICORN_PORT")
    PROJECT_NAME: str = Field("FastAPI Auth Service", min_length=1)

    class Config:
        env_file = Path(__file__).resolve().parents[1] / "env.example"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
