from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from firebase_admin import firestore

class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_PORT: int = 8000
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    AUTH_KEY: str
    REFRESH_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRES_IN: int
    SONG_REPORTED_WEBHOOK: str
    FIREBASE_KEY_FILENAME: str

    @property
    def DATABASE_URI(self) -> str:
        return str(PostgresDsn.build(
            scheme='postgresql',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            path=f'{self.POSTGRES_DB or ""}',
        ))

    @property
    def ASYNC_DATABASE_URI(self) -> str:
        return str(PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            path=f'{self.POSTGRES_DB or ""}',
        ))

    class Config:
        case_sensitive = True
        env_file = '.env'

settings = Settings.parse_obj({})