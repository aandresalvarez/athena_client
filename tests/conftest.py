"""
Test fixtures and configuration for Athena client tests.
"""

from unittest.mock import Mock, patch

import pytest

from athena_client import Athena
from athena_client.client import AthenaClient


@pytest.fixture
def mock_http_client():
    """Mock HttpClient to avoid making real API calls."""
    mock_instance = Mock()
    with patch("athena_client.client.HttpClient", return_value=mock_instance):
        # Disable retry mechanism for testing
        mock_instance.max_retries = 0
        yield mock_instance


@pytest.fixture
def athena_client():
    """Create a mock Athena client for testing."""
    mock_instance = Mock()
    with patch("athena_client.client.HttpClient", return_value=mock_instance):
        # Disable retry mechanism for testing
        mock_instance.max_retries = 0
        client = AthenaClient()
        client.http = mock_instance
        yield client


@pytest.fixture
def athena_facade(mock_http_client):
    """Get a mocked Athena facade."""
    facade = Athena()
    return facade
