import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DHL_API_KEY: str | None = None

    POSTGRES_DATABASE: str | None = None
    POSTGRES_USERNAME: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_PORT: str | None = None
    POSTGRES_HOST: str | None = None

    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str | None = None
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: str | None = None

    # Check if running in Docker and choose the appropriate .env file
    env_file: str = './secrets/.env.docker' if os.getenv("DOCKER_ENV") else './secrets/.env'

    model_config = SettingsConfigDict(env_file=env_file, extra='allow')
