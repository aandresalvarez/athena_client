"""
Authentication module for the Athena client.

This module handles Bearer token and HMAC authentication for the Athena API.
"""
from typing import Dict

from .settings import get_settings


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
    if s.ATHENA_TOKEN is None:
        return {}
        
    hdrs = {
        "X-Athena-Auth": f"Bearer {s.ATHENA_TOKEN}",
        "X-Athena-Client-Id": s.ATHENA_CLIENT_ID or "athena-client",
    }
    
    if s.ATHENA_PRIVATE_KEY:  
        # Import here for optional dependency
        try:
            from base64 import b64encode
            from datetime import datetime
            from cryptography.hazmat.primitives import hashes, serialization
            
            nonce = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            to_sign = f"{method}\n{url}\n\n{nonce}\n{body.decode()}"
            key = serialization.load_pem_private_key(
                s.ATHENA_PRIVATE_KEY.encode(), password=None
            )
            sig = key.sign(to_sign.encode(), hashes.SHA256())
            hdrs.update({
                "X-Athena-Nonce": nonce,
                "X-Athena-Hmac": b64encode(sig).decode()
            })
        except ImportError:
            import logging
            logging.warning(
                "cryptography package is required for HMAC signing. "
                "Install with 'pip install \"athena-client[crypto]\"'"
            )
            
    return hdrs
