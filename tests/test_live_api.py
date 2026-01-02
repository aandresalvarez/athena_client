"""Live API integration tests for Athena."""

import os
from typing import Iterator

import pytest

from athena_client import Athena
from athena_client.settings import get_settings


@pytest.fixture
def live_athena_client() -> Iterator[Athena]:
    """Create an Athena client without authentication."""
    settings = get_settings()
    original_token = settings.ATHENA_TOKEN
    original_client_id = settings.ATHENA_CLIENT_ID
    original_private_key = settings.ATHENA_PRIVATE_KEY
    settings.ATHENA_TOKEN = None
    settings.ATHENA_CLIENT_ID = None
    settings.ATHENA_PRIVATE_KEY = None
    try:
        yield Athena()
    finally:
        settings.ATHENA_TOKEN = original_token
        settings.ATHENA_CLIENT_ID = original_client_id
        settings.ATHENA_PRIVATE_KEY = original_private_key


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ATHENA_LIVE_TESTS"),
    reason="Live API tests require ATHENA_LIVE_TESTS=true",
)
class TestLiveApi:
    """Run lightweight checks against the real Athena API."""

    def test_search_live(self, live_athena_client: Athena) -> None:
        """Search should return at least one concept."""
        results = live_athena_client.search("aspirin", size=1)
        concepts = results.all()
        assert concepts
        assert concepts[0].name

    def test_details_live(self, live_athena_client: Athena) -> None:
        """Details should return a known concept."""
        details = live_athena_client.details(1127433)
        assert details.id == 1127433
        assert details.name
