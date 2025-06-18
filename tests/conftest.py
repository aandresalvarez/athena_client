"""
Test fixtures and configuration for athena-client tests.
"""
from unittest.mock import patch

import pytest

from athena_client import Athena
from athena_client.client import AthenaClient


@pytest.fixture
def mock_http_client():
    """Mock HttpClient to avoid making real API calls."""
    with patch("athena_client.client.HttpClient") as mock:
        yield mock


@pytest.fixture
def athena_client(mock_http_client):
    """Get a mocked Athena client."""
    client = AthenaClient()
    return client


@pytest.fixture
def athena_facade(mock_http_client):
    """Get a mocked Athena facade."""
    facade = Athena()
    return facade
