"""
Test fixtures and configuration for Athena client tests.
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from athena_client import Athena
from athena_client.async_client import AsyncHttpClient
from athena_client.client import AthenaClient

_ASYNC_HTTP_CLIENTS = []
_ORIGINAL_ASYNC_HTTP_INIT = AsyncHttpClient.__init__


def _tracking_async_http_init(self, *args, **kwargs) -> None:
    _ORIGINAL_ASYNC_HTTP_INIT(self, *args, **kwargs)
    _ASYNC_HTTP_CLIENTS.append(self)


def pytest_configure(config: pytest.Config) -> None:
    AsyncHttpClient.__init__ = _tracking_async_http_init  # type: ignore[assignment]


def pytest_sessionfinish(
    session: pytest.Session, exitstatus: int
) -> None:
    if not _ASYNC_HTTP_CLIENTS:
        return

    async def _close_clients() -> None:
        for client in _ASYNC_HTTP_CLIENTS:
            try:
                if hasattr(client, "client") and not client.client.is_closed:
                    await client.aclose()
            except Exception:
                pass

    try:
        asyncio.run(_close_clients())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_close_clients())
        loop.close()
    _ASYNC_HTTP_CLIENTS.clear()


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
