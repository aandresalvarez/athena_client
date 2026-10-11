"""Athena JavaScript session-cookie generation.

Athena's public frontend creates ``athena_js_session`` in JavaScript before
calling the API. The server no longer seeds the former ``athena_session``
cookie, so non-browser clients must create the current cookie themselves.
"""

from __future__ import annotations

import os
import platform
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator, Optional

ATHENA_JS_SESSION_COOKIE_NAME = "athena_js_session"

_ALGORITHM_MARKER = "athena-js-2026"
_UINT32_MASK = 0xFFFFFFFF


def _browser_platform() -> str:
    """Return a browser-like ``navigator.platform`` value."""
    system = platform.system()
    machine = platform.machine()
    if system == "Darwin":
        return "MacIntel"
    if system == "Windows":
        return "Win32"
    if system == "Linux":
        return f"Linux {machine}" if machine else "Linux"
    return system or machine


def _timezone_offset_minutes() -> int:
    """Return the local offset using JavaScript's ``getTimezoneOffset`` sign."""
    local_offset = datetime.now().astimezone().utcoffset()
    if local_offset is None:
        return 0
    return -int(local_offset.total_seconds() // 60)


@dataclass(frozen=True)
class BrowserFingerprint:
    """Browser properties included in Athena's cookie hash input."""

    user_agent: str
    screen_width: int
    screen_height: int
    timezone_offset_minutes: int
    language: str
    color_depth: int
    hardware_concurrency: int
    browser_platform: str
    performance_milliseconds: int
    canvas_hash: str

    @classmethod
    def for_http_client(cls, user_agent: str) -> "BrowserFingerprint":
        """Create a browser-compatible fingerprint for a Python HTTP client."""
        return cls(
            user_agent=user_agent,
            screen_width=1920,
            screen_height=1080,
            timezone_offset_minutes=_timezone_offset_minutes(),
            language="en-US",
            color_depth=24,
            hardware_concurrency=os.cpu_count() or 1,
            browser_platform=_browser_platform(),
            performance_milliseconds=int(time.perf_counter() * 1000),
            canvas_hash="no-canvas",
        )

    def serialize(self) -> str:
        """Serialize fields in the order used by Athena's frontend."""
        return "|".join(
            (
                self.user_agent,
                str(self.screen_width),
                str(self.screen_height),
                str(self.timezone_offset_minutes),
                self.language,
                str(self.color_depth),
                str(self.hardware_concurrency),
                self.browser_platform,
                str(self.performance_milliseconds),
                self.canvas_hash,
            )
        )


def _javascript_utf16_code_units(value: str) -> Iterator[int]:
    """Yield code units equivalent to JavaScript's ``charCodeAt``."""
    encoded = value.encode("utf-16-le", errors="surrogatepass")
    for index in range(0, len(encoded), 2):
        yield encoded[index] | (encoded[index + 1] << 8)


def javascript_djb2_xor(value: str) -> str:
    """Return Athena's eight-character unsigned DJB2-XOR hash."""
    hash_value = 5381
    for code_unit in _javascript_utf16_code_units(value):
        hash_value = (((hash_value << 5) + hash_value) ^ code_unit) & _UINT32_MASK
    return f"{hash_value:08x}"


def _base36(value: int) -> str:
    """Encode a non-negative integer as lowercase base36."""
    if value < 0:
        raise ValueError("value must be non-negative")

    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    if value == 0:
        return "0"

    digits = []
    while value:
        value, remainder = divmod(value, 36)
        digits.append(alphabet[remainder])
    return "".join(reversed(digits))


def create_athena_js_session(
    user_agent: str,
    *,
    now: Optional[datetime] = None,
    nonce: Optional[str] = None,
    fingerprint: Optional[BrowserFingerprint] = None,
    previous_utc_day: bool = False,
) -> str:
    """Create an ``athena_js_session`` value using Athena's frontend algorithm.

    Athena's frontend accepts cookies dated today or yesterday. The
    ``previous_utc_day`` option supports servers whose local date temporarily
    lags UTC after the UTC day boundary.
    """
    effective_now = now or datetime.now(timezone.utc)
    if effective_now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if previous_utc_day:
        effective_now -= timedelta(days=1)

    date_stamp = effective_now.astimezone(timezone.utc).strftime("%Y%m%d")
    effective_nonce = nonce if nonce is not None else _base36(secrets.randbits(53))
    effective_fingerprint = fingerprint or BrowserFingerprint.for_http_client(
        user_agent
    )
    hash_input = "::".join(
        (
            date_stamp,
            _ALGORITHM_MARKER,
            effective_fingerprint.serialize(),
            effective_nonce,
        )
    )
    return f"{date_stamp}_{javascript_djb2_xor(hash_input)}"


def is_athena_js_session_current(
    value: Optional[str],
    *,
    now: Optional[datetime] = None,
) -> bool:
    """Return whether a cookie matches Athena's current-or-previous-day rule."""
    if value is None:
        return False

    effective_now = now or datetime.now(timezone.utc)
    if effective_now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    parts = value.split("_")
    if len(parts) != 2:
        return False

    date_stamp, hash_value = parts
    if len(hash_value) != 8 or any(
        character not in "0123456789abcdef" for character in hash_value
    ):
        return False

    current_utc = effective_now.astimezone(timezone.utc)
    accepted_dates = {
        current_utc.strftime("%Y%m%d"),
        (current_utc - timedelta(days=1)).strftime("%Y%m%d"),
    }
    return date_stamp in accepted_dates
