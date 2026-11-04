from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

# The backend/ folder. Paths below are built from it so the app works
# no matter which folder you start uvicorn from.


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "dev" enables the X-Debug-IP fake-IP header. Use "prod" anywhere else.
    app_env: str = os.getenv("APP_ENV", "prod")
    database_url: str = os.getenv("DATABASE_URL")
    geoip_db_path: str = os.getenv("GEOIP_DB_PATH", "GeoLite2-City.mmdb")
    cors_origins: str = os.getenv("CORS_ORIGINS") 
    trust_proxy: bool = False  # Set to True if running behind a reverse proxy (e.g. Nginx)
    admin_key: str = os.getenv("ADMIN_KEY")  # Must be set in .env for production

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_dev(self) -> bool:
        return self.app_env.lower() == "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()
