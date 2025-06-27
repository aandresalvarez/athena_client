"""
Tests for settings module to ensure proper handling of environment variables.
"""

import os
from unittest.mock import patch

from athena_client.settings import (
    _Settings,
    clear_settings_cache,
    get_settings,
    reload_settings,
)


class TestSettingsEnvironmentVariables:
    """Test settings behavior with various environment variable configurations."""

    def setup_method(self):
        """Clear settings cache before each test to ensure clean state."""
        clear_settings_cache()

    def test_settings_initialization_without_external_env_vars(self):
        """Test that settings initialize correctly without unrelated env vars."""
        # Clear any existing environment variables that might interfere
        with patch.dict(os.environ, {}, clear=True):
            settings = get_settings()
            assert settings.ATHENA_BASE_URL == "https://athena.ohdsi.org/api/v1"
            assert settings.ATHENA_TIMEOUT_SECONDS == 30

    def test_settings_with_external_google_credentials(self):
        """Test that settings work when GOOGLE_APPLICATION_CREDENTIALS is set."""
        test_env = {
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
            "ATHENA_BASE_URL": "https://custom.athena.org/api/v1",
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            # Should not fail and should use the custom ATHENA_BASE_URL
            assert settings.ATHENA_BASE_URL == "https://custom.athena.org/api/v1"
            assert settings.ATHENA_TIMEOUT_SECONDS == 30

    def test_settings_with_external_openai_key(self):
        """Test that settings work when OPENAI_API_KEY is set."""
        test_env = {
            "OPENAI_API_KEY": "sk-proj-vO1urVisRlM1Upkk...AtK0BzkoftVcCEhpvShK4wA",
            "ATHENA_TOKEN": "test-token",
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            # Should not fail and should use the ATHENA_TOKEN
            assert settings.ATHENA_TOKEN == "test-token"
            assert settings.ATHENA_BASE_URL == "https://athena.ohdsi.org/api/v1"

    def test_settings_with_multiple_external_vars(self):
        """Test that settings work with multiple external environment variables."""
        test_env = {
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
            "OPENAI_API_KEY": "sk-proj-vO1urVisRlM1Upkk...AtK0BzkoftVcCEhpvShK4wA",
            "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
            "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "ATHENA_TOKEN": "test-token",
            "ATHENA_TIMEOUT_SECONDS": "60",
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            # Should not fail and should use the athena-specific settings
            assert settings.ATHENA_TOKEN == "test-token"
            assert settings.ATHENA_TIMEOUT_SECONDS == 60
            assert settings.ATHENA_BASE_URL == "https://athena.ohdsi.org/api/v1"

    def test_settings_extra_fields_ignored(self):
        """Test that extra fields are properly ignored."""
        # Create a settings instance with extra fields
        test_env = {
            "EXTRA_FIELD_1": "value1",
            "EXTRA_FIELD_2": "value2",
            "ATHENA_BASE_URL": "https://test.athena.org/api/v1",
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            # Should not fail and should only use ATHENA_ prefixed fields
            assert settings.ATHENA_BASE_URL == "https://test.athena.org/api/v1"

            # Verify that extra fields are not accessible
            assert not hasattr(settings, "EXTRA_FIELD_1")
            assert not hasattr(settings, "EXTRA_FIELD_2")

    def test_settings_cache_behavior(self):
        """Test that settings caching works correctly with environment changes."""
        # First call with default environment
        with patch.dict(os.environ, {}, clear=True):
            settings1 = get_settings()
            assert settings1.ATHENA_BASE_URL == "https://athena.ohdsi.org/api/v1"

        # Clear cache and call with custom environment
        clear_settings_cache()

        with patch.dict(
            os.environ,
            {"ATHENA_BASE_URL": "https://custom.athena.org/api/v1"},
            clear=True,
        ):
            settings2 = get_settings()
            assert settings2.ATHENA_BASE_URL == "https://custom.athena.org/api/v1"

    def test_settings_model_config(self):
        """Test that the model configuration is set correctly."""
        # Verify that the model config ignores extra fields
        assert _Settings.model_config.get("extra") == "ignore"
        assert _Settings.model_config.get("env_file") == ".env"
        assert _Settings.model_config.get("env_prefix") == ""

    def test_settings_all_defined_fields(self):
        """Test that all defined settings fields are accessible."""
        settings = get_settings()

        # Test all the defined fields exist and have expected types
        assert isinstance(settings.ATHENA_BASE_URL, str)
        assert isinstance(settings.ATHENA_TOKEN, (str, type(None)))
        assert isinstance(settings.ATHENA_CLIENT_ID, (str, type(None)))
        assert isinstance(settings.ATHENA_PRIVATE_KEY, (str, type(None)))
        assert isinstance(settings.ATHENA_TIMEOUT_SECONDS, int)
        assert isinstance(settings.ATHENA_SEARCH_TIMEOUT_SECONDS, int)
        assert isinstance(settings.ATHENA_GRAPH_TIMEOUT_SECONDS, int)
        assert isinstance(settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS, int)
        assert isinstance(settings.ATHENA_MAX_RETRIES, int)
        assert isinstance(settings.ATHENA_BACKOFF_FACTOR, float)
        assert isinstance(settings.ATHENA_DEFAULT_PAGE_SIZE, int)
        assert isinstance(settings.ATHENA_MAX_PAGE_SIZE, int)
        assert isinstance(settings.ATHENA_LARGE_QUERY_THRESHOLD, int)
        assert isinstance(settings.ATHENA_SHOW_PROGRESS, bool)
        assert isinstance(settings.ATHENA_PROGRESS_UPDATE_INTERVAL, float)
        assert isinstance(settings.ATHENA_AUTO_CHUNK_LARGE_QUERIES, bool)
        assert isinstance(settings.ATHENA_CHUNK_SIZE, int)
        assert isinstance(settings.ATHENA_MAX_CONCURRENT_CHUNKS, int)

    def test_clear_settings_cache(self):
        """Test that clear_settings_cache works correctly."""
        # Get initial settings
        settings1 = get_settings()

        # Clear cache
        clear_settings_cache()

        # Get settings again - should be a new instance
        settings2 = get_settings()

        # They should be different instances
        assert settings1 is not settings2

    def test_reload_settings(self):
        """Test that reload_settings works correctly."""
        # Get initial settings
        settings1 = get_settings()

        # Reload settings
        settings2 = reload_settings()

        # They should be different instances
        assert settings1 is not settings2

    def test_external_env_vars_do_not_cause_errors(self):
        """Test that external environment variables don't cause validation errors."""
        test_env = {
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json",
            "OPENAI_API_KEY": "sk-proj-vO1urVisRlM1Upkk...AtK0BzkoftVcCEhpvShK4wA",
            "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
            "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "DATABASE_URL": "postgresql://user:pass@localhost/db",
            "REDIS_URL": "redis://localhost:6379",
            "ATHENA_TOKEN": "test-token",
        }

        with patch.dict(os.environ, test_env, clear=True):
            # This should not raise any validation errors
            settings = get_settings()
            assert settings.ATHENA_TOKEN == "test-token"
            assert settings.ATHENA_BASE_URL == "https://athena.ohdsi.org/api/v1"

    def test_only_athena_prefixed_vars_are_used(self):
        """Test that only ATHENA_ prefixed environment variables are used."""
        test_env = {
            "ATHENA_TOKEN": "athena-token",
            "ATHENA_BASE_URL": "https://custom.athena.org/api/v1",
            "TOKEN": "other-token",  # This should be ignored
            "BASE_URL": "https://other.org/api/v1",  # This should be ignored
        }

        with patch.dict(os.environ, test_env, clear=True):
            settings = get_settings()
            assert settings.ATHENA_TOKEN == "athena-token"
            assert settings.ATHENA_BASE_URL == "https://custom.athena.org/api/v1"

            # Verify that non-ATHENA_ prefixed variables are not accessible
            assert not hasattr(settings, "TOKEN")
            assert not hasattr(settings, "BASE_URL")
