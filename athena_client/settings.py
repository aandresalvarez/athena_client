"""
Settings module for the Athena client.

This module provides configuration settings loaded from environment variables
or .env files using pydantic-settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """
    Configuration settings for the Athena client.
    
    Settings can be provided via environment variables, .env file, or defaults.
    """
    
    ATHENA_BASE_URL: str = "https://athena.ohdsi.org/api/v1"
    ATHENA_TOKEN: Optional[str] = None
    ATHENA_CLIENT_ID: Optional[str] = None
    ATHENA_PRIVATE_KEY: Optional[str] = None
    ATHENA_TIMEOUT_SECONDS: int = 10
    ATHENA_MAX_RETRIES: int = 3
    ATHENA_BACKOFF_FACTOR: float = 0.3
    
    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


@lru_cache
def get_settings() -> _Settings:
    """
    Get the settings singleton.
    
    Returns:
        Cached instance of _Settings.
    """
    return _Settings()  # cached singleton
