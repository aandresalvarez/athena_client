"""
Centralized User-Agent strings and header construction for the Athena client to avoid duplication
and ensure consistency between sync and async implementations.
"""

from typing import Dict

# List of browser-like User-Agents for fallback (updated to 2025 versions)
USER_AGENTS = [
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) "
        "Gecko/20100101 Firefox/133.0"
    ),
]


def get_default_headers(user_agent_idx: int = 0) -> Dict[str, str]:
    """
    Construct default browser-like headers for Athena API requests.

    Args:
        user_agent_idx: Index of the User-Agent string to use from USER_AGENTS.

    Returns:
        Dictionary of default headers.
    """
    # Ensure index is within range
    idx = user_agent_idx % len(USER_AGENTS)

    return {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": USER_AGENTS[idx],
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://athena.ohdsi.org/search-terms/terms",
        "Origin": "https://athena.ohdsi.org",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Connection": "keep-alive",
    }
