"""
Authentication module for the Athena client.

This module handles Bearer token and HMAC authentication for the Athena API.
"""

import logging
from base64 import b64encode
from datetime import datetime
from typing import Any, Dict

from cryptography.hazmat.primitives import hashes, serialization

from .settings import get_settings

logger = logging.getLogger(__name__)


def build_headers(method: str, url: str, body: bytes) -> Dict[str, str]:
    """
    Build authentication headers for Athena API requests.

    If a token is supplied, adds Bearer authentication.
    If a private key is supplied, adds HMAC signature.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        body: Request body as bytes

    Returns:
        Dictionary of headers to add to the request
    """
    s = get_settings()

    # Start with empty headers - authentication is optional
    hdrs = {}

    # Add Bearer token if available
    if s.ATHENA_TOKEN:
        hdrs["X-Athena-Auth"] = f"Bearer {s.ATHENA_TOKEN}"
        hdrs["X-Athena-Client-Id"] = s.ATHENA_CLIENT_ID or "athena-client"
        logger.debug("Bearer token authentication headers added")
    else:
        logger.debug("No API token provided; proceeding without Authorization header")

    # Add HMAC signature if private key is available
    if s.ATHENA_PRIVATE_KEY:
        try:
            nonce = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            to_sign = f"{method}\n{url}\n\n{nonce}\n{body.decode()}"
            key = serialization.load_pem_private_key(
                s.ATHENA_PRIVATE_KEY.encode(), password=None
            )
            signing_key: Any = key
            sig = signing_key.sign(to_sign.encode(), hashes.SHA256())
            hdrs.update(
                {"X-Athena-Nonce": nonce, "X-Athena-Hmac": b64encode(sig).decode()}
            )
            logger.debug("HMAC signature headers added")
        except ImportError:
            logger.warning(
                "cryptography package is required for HMAC signing. "
                "Install with 'pip install \"athena-client[crypto]\"'"
            )
        except Exception as e:
            logger.error(f"Error generating HMAC signature: {e}")

    return hdrs
