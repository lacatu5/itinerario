from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    return Path(__file__).parent.parent


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class CloudSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(get_project_root() / ".env"), env_file_encoding="utf-8", extra="allow"
    )

    ENVIRONMENT: Environment = Environment.LOCAL
    GOOGLE_CLOUD_PROJECT: str | None = None
    CLOUD_STORAGE_BUCKET: str = "demo-bucket-itinerario"
    FIREBASE_PROJECT_ID: str = "demo-project-id"
    STORAGE_EMULATOR_HOST: str = "localhost:9099"
    FIRESTORE_EMULATOR_HOST: str = "localhost:8080"
    FIREBASE_AUTH_EMULATOR_HOST: str = "localhost:9099"

    @property
    def is_local(self) -> bool:
        return self.ENVIRONMENT == Environment.LOCAL

    @property
    def is_dev(self) -> bool:
        return self.ENVIRONMENT == Environment.DEV

    @property
    def is_prod(self) -> bool:
        return self.ENVIRONMENT == Environment.PROD


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(get_project_root() / ".env"), env_file_encoding="utf-8", extra="allow"
    )

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    CLOUD_SQL_CONNECTION_NAME: str | None = None
    DATABASE_URL: str | None = None


class CentrifugoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(get_project_root() / ".env"), env_file_encoding="utf-8", extra="allow"
    )

    CENTRIFUGO_API_URL: str
    CENTRIFUGO_API_KEY: str
    CENTRIFUGO_HMAC_SECRET_KEY: str
    CENTRIFUGO_WS_URL: str


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(get_project_root() / ".env"), env_file_encoding="utf-8", extra="allow"
    )

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    WORKERS: int = 1


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(get_project_root() / ".env"), env_file_encoding="utf-8", extra="allow"
    )

    AVIATIONSTACK_API_KEY: str | None = None
    AVIATIONSTACK_BASE_URL: str = "http://api.aviationstack.com/v1"
    AVIATIONSTACK_TIMEOUT: float = 15.0

    OPEN_METEO_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1"
    OPEN_METEO_AVAILABLE: str = "true"
    OPEN_METEO_TIMEOUT: float = 10.0

    FCDO_FEED_URL: str = "https://www.gov.uk/foreign-travel-advice.atom"
    FCDO_TIMEOUT: float = 30.0

    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0


class FeatureFlags(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(get_project_root() / ".env"), env_file_encoding="utf-8", extra="allow"
    )

    ENABLE_MOCK_DATA: bool = False
    ENABLE_HEALTH_CHECKS: bool = True

    @property
    def use_live_apis(self) -> bool:
        return not self.ENABLE_MOCK_DATA


config = CloudSettings()
db_settings = DatabaseSettings()
centrifugo_settings = CentrifugoSettings()
service_settings = ServiceSettings()
api_settings = APISettings()
feature_flags = FeatureFlags()
