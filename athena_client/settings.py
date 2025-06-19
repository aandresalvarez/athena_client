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
    
    # Enhanced timeout configuration for different operations
    ATHENA_TIMEOUT_SECONDS: int = 30  # Increased default timeout
    ATHENA_SEARCH_TIMEOUT_SECONDS: int = 45  # Longer timeout for search operations
    ATHENA_GRAPH_TIMEOUT_SECONDS: int = 60  # Even longer for graph operations
    ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS: int = 45  # For relationship queries
    
    # Retry configuration
    ATHENA_MAX_RETRIES: int = 3
    ATHENA_BACKOFF_FACTOR: float = 0.3
    
    # Pagination configuration
    ATHENA_DEFAULT_PAGE_SIZE: int = 20
    ATHENA_MAX_PAGE_SIZE: int = 1000
    ATHENA_LARGE_QUERY_THRESHOLD: int = 100  # Threshold for "large" queries
    
    # Progress and user experience
    ATHENA_SHOW_PROGRESS: bool = True
    ATHENA_PROGRESS_UPDATE_INTERVAL: float = 2.0  # Seconds between progress updates
    
    # Large query handling
    ATHENA_AUTO_CHUNK_LARGE_QUERIES: bool = True
    ATHENA_CHUNK_SIZE: int = 50  # Size for chunking large queries
    ATHENA_MAX_CONCURRENT_CHUNKS: int = 3  # Max concurrent chunk requests

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


@lru_cache
def get_settings() -> _Settings:
    """
    Get the settings singleton.

    Returns:
        Cached instance of _Settings.
    """
    return _Settings()  # cached singleton
