"""Tests for Athena JavaScript session-cookie generation."""

from datetime import datetime, timezone
from typing import Optional

import pytest

from athena_client.athena_session import (
    BrowserFingerprint,
    create_athena_js_session,
    is_athena_js_session_current,
    javascript_djb2_xor,
)


def test_javascript_hash_matches_ascii_reference() -> None:
    """The Python hash should match Athena's JavaScript output."""
    assert javascript_djb2_xor("Athena OHDSI") == "c4df42cb"


def test_javascript_hash_uses_utf16_code_units() -> None:
    """Non-BMP input should match JavaScript's charCodeAt behavior."""
    assert javascript_djb2_xor("Athena 🧬") == "8a41eea0"


def test_cookie_matches_javascript_reference() -> None:
    """Cookie construction should match a fixed frontend test vector."""
    fingerprint = BrowserFingerprint(
        user_agent="Test/1.0",
        screen_width=1920,
        screen_height=1080,
        timezone_offset_minutes=420,
        language="en-US",
        color_depth=24,
        hardware_concurrency=8,
        browser_platform="MacIntel",
        performance_milliseconds=1234,
        canvas_hash="no-canvas",
    )

    cookie = create_athena_js_session(
        "Test/1.0",
        now=datetime(2026, 10, 10, 23, 0, tzinfo=timezone.utc),
        nonce="fixednonce",
        fingerprint=fingerprint,
    )

    assert cookie == "20261010_d07b6da0"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20261010_d07b6da0", True),
        ("20261009_d07b6da0", True),
        ("20261008_d07b6da0", False),
        ("20261010", False),
        ("20261010_not-hex!", False),
        ("20261010_D07B6DA0", False),
        (None, False),
    ],
)
def test_cookie_freshness_matches_frontend_rule(
    value: Optional[str],
    expected: bool,
) -> None:
    """Only well-formed values from today or yesterday should be current."""
    now = datetime(2026, 10, 10, 23, 0, tzinfo=timezone.utc)

    assert is_athena_js_session_current(value, now=now) is expected


def test_naive_datetime_is_rejected() -> None:
    """Ambiguous local datetimes should not be accepted."""
    with pytest.raises(ValueError, match="timezone-aware"):
        create_athena_js_session("Test/1.0", now=datetime(2026, 10, 10))
