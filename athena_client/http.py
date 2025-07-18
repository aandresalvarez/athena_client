"""
HTTP client implementation for Athena API.

This module provides HTTP clients for making requests to the Athena API,
with features like retry, backoff, and timeout handling.
"""

import json
import logging
import random
import time
from typing import Any, Dict, Optional, Tuple, TypeVar, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import build_headers
from .exceptions import (
    AthenaError,
    AuthenticationError,
    ClientError,
    NetworkError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .settings import get_settings

# Type variable for generic response
T = TypeVar("T")

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Synchronous HTTP client for making requests to the Athena API.

    Features:
    - Automatic retry with exponential backoff
    - Custom timeout handling
    - Authentication header generation
    - Error handling and mapping to typed exceptions
    - Robust logging and debugging
    - Custom User-Agent and headers
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        enable_throttling: bool = True,
        throttle_delay_range: Tuple[float, float] = (0.1, 0.3),
    ) -> None:
        """
        Initialize the HTTP client with configuration.

        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
            enable_throttling: Whether to throttle requests to be respectful
                to the server
            throttle_delay_range: Range of delays for throttling (min, max)
                in seconds
        """
        settings = get_settings()

        # Use provided values or fall back to settings
        self.base_url = base_url or settings.ATHENA_BASE_URL

        # Set up token and HMAC if provided
        if token is not None:
            settings.ATHENA_TOKEN = token
        if client_id is not None:
            settings.ATHENA_CLIENT_ID = client_id
        if private_key is not None:
            settings.ATHENA_PRIVATE_KEY = private_key

        self.timeout = timeout or settings.ATHENA_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.ATHENA_MAX_RETRIES
        self.backoff_factor = backoff_factor or settings.ATHENA_BACKOFF_FACTOR
        self.enable_throttling = enable_throttling
        self.throttle_delay_range = throttle_delay_range

        # Create session with retry configuration
        self.session = self._create_session()

        # Set up default headers
        self._setup_default_headers()

        logger.debug("HttpClient initialized with base URL: %s", self.base_url)

    def _create_session(self) -> requests.Session:
        """
        Create and configure a requests Session with enhanced retry logic.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        # Allow a limited number of redirects to handle necessary API redirects
        # while preventing infinite redirect loops
        session.max_redirects = 2

        # Enhanced retry strategy for better handling of rate limiting
        # and server overload
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            # Retry on rate limiting (429), server errors (5xx), and temporary failures
            status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
            # Also retry on connection errors and timeouts
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            # Respect Retry-After headers from server
            respect_retry_after_header=True,
            # Exponential backoff with jitter to prevent thundering herd
            raise_on_status=False,  # Let us handle status codes ourselves
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    # List of browser-like User-Agents for fallback
    _USER_AGENTS = [
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
            "Gecko/20100101 Firefox/120.0"
        ),
    ]

    def _setup_default_headers(self, user_agent_idx: int = 0) -> None:
        """Set up default headers for all requests, with optional User-Agent index."""
        default_headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            "User-Agent": self._USER_AGENTS[user_agent_idx],
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://athena.ohdsi.org/",
            "Connection": "keep-alive",
        }
        self.session.headers.clear()
        self.session.headers.update(default_headers)
        logger.debug("Default headers set: %s", default_headers)

    def _throttle_request(self) -> None:
        """
        Implement request throttling to prevent overwhelming the server.

        This adds a small delay between requests to be respectful to the API.
        """
        if not self.enable_throttling:
            return

        # Add a small random delay between requests
        # This prevents overwhelming the server with rapid requests
        delay = random.uniform(  # nosec B311
            self.throttle_delay_range[0], self.throttle_delay_range[1]
        )
        time.sleep(delay)

        logger.debug(f"Request throttled for {delay:.3f} seconds")

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """
        Handle rate limiting with intelligent backoff.

        Args:
            response: HTTP response that indicates rate limiting
        """
        # Get retry-after header if available
        retry_after = response.headers.get("Retry-After")

        if retry_after:
            try:
                wait_time = int(retry_after)
                logger.info(
                    f"Rate limited. Waiting {wait_time} seconds as requested by server."
                )
                time.sleep(wait_time)
            except ValueError:
                # If Retry-After is not a number, use exponential backoff
                wait_time = 60  # Default to 1 minute
                logger.info(f"Rate limited. Waiting {wait_time} seconds (default).")
                time.sleep(wait_time)
        else:
            # No Retry-After header, use exponential backoff
            wait_time = 60  # Default to 1 minute
            logger.info(
                f"Rate limited. Waiting {wait_time} seconds (exponential backoff)."
            )
            time.sleep(wait_time)

    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.

        Args:
            path: API path

        Returns:
            Full URL
        """
        # Handle paths that start with / to ensure they're appended correctly
        if path.startswith("/"):
            # Remove the leading / and join with base_url
            path = path[1:]

        # Ensure base_url doesn't end with / and path doesn't start with /
        if self.base_url.endswith("/"):
            base = self.base_url[:-1]
        else:
            base = self.base_url

        if path.startswith("/"):
            path = path[1:]

        full_url = f"{base}/{path}"

        logger.debug(
            f"Building URL: base_url='{self.base_url}', path='{path}' "
            f"-> full_url='{full_url}'"
        )
        return full_url

    def _normalize_params(
        self, params: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, str]]:
        """
        Normalize parameters to ensure all values are strings.

        Args:
            params: Query parameters

        Returns:
            Normalized parameters with string values
        """
        if params is None:
            return None

        normalized = {}
        for key, value in params.items():
            if value is not None:
                normalized[key] = str(value)
        return normalized

    def _handle_response(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response from requests
            url: Full URL that was requested

        Returns:
            Parsed JSON response

        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
            APIError: For API-specific error responses
        """
        # Log raw response for debugging
        raw_response_text = response.text
        logger.debug(f"Raw response text from {url}: {raw_response_text[:1000]}...")

        try:
            response.raise_for_status()

            # Attempt to parse JSON after logging raw text
            data = response.json()
            logger.debug("Successfully parsed JSON from %s", url)
            return data

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else "N/A"
            text = e.response.text if e.response else "No response content"

            # Try to parse the error response as JSON to extract API error details
            api_message = None

            try:
                if e.response and e.response.text:
                    error_data = e.response.json()
                    api_message = error_data.get("errorMessage")
            except (ValueError, AttributeError):
                pass

            # Create a more descriptive error message
            if api_message:
                msg = f"API Error {status}: {api_message}"
            else:
                msg = f"HTTP error {status} when accessing {url}"
                if text and text != "No response content":
                    msg += f": {text[:200]}"

            logger.error(msg)
            logger.exception(e)

            # Raise specific exception types based on status code
            if status == 401:
                raise AuthenticationError(
                    f"Authentication failed: {msg}",
                    status_code=response.status_code,
                    response=response.text,
                    url=url,
                ) from e
            elif status == 403:
                raise ClientError(
                    f"Access forbidden: {msg}",
                    status_code=response.status_code,
                    response=response.text,
                    url=url,
                ) from e
            elif status == 404:
                raise ClientError(
                    f"Resource not found: {msg}",
                    status_code=response.status_code,
                    response=response.text,
                    url=url,
                ) from e
            elif status == 429:
                raise RateLimitError(
                    f"Rate limit exceeded: {msg}",
                    status_code=response.status_code,
                    response=response.text,
                    url=url,
                ) from e
            elif 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {msg}",
                    status_code=response.status_code,
                    response=response.text,
                    url=url,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {msg}",
                    status_code=response.status_code,
                    response=response.text,
                    url=url,
                ) from e
            else:
                raise

        except json.JSONDecodeError as e:
            msg = (
                f"Invalid JSON response from {url}: {e}. "
                f"Raw text was: {raw_response_text[:1000]}..."
            )
            logger.error(msg)
            logger.exception(e)
            raise ValidationError(
                f"Invalid JSON response: {e}", validation_details=str(e)
            ) from e

        except Exception as e:
            msg = f"An unexpected error occurred when accessing {url}: {e}"
            logger.error(msg)
            logger.exception(e)
            raise AthenaError(msg, error_code="UNEXPECTED_ERROR") from e

    def request(
        self,
        method: str,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make an HTTP request to the Athena API with enhanced retry and throttling.
        Tries multiple User-Agents and browser-like headers if the server returns
        a redirect loop or non-JSON response.
        """
        url = self._build_url(path)
        body_bytes = b""
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")
        auth_headers = build_headers(method, url, body_bytes)
        headers = dict(self.session.headers)
        headers.update(auth_headers)
        normalized_params = self._normalize_params(params)
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(
            f"[{correlation_id}] {method} {url} with params: {normalized_params}"
        )
        self._throttle_request()

        last_exception: Optional[Exception] = None
        for agent_idx, agent in enumerate(self._USER_AGENTS):
            if agent_idx > 0:
                logger.info(f"Retrying with fallback User-Agent: {agent}")
                self._setup_default_headers(user_agent_idx=agent_idx)
                headers = dict(self.session.headers)
                headers.update(auth_headers)
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=normalized_params,
                    data=body_bytes if data is not None else None,
                    headers=headers,
                    timeout=self.timeout,
                )
                logger.debug(
                    f"[{correlation_id}] {response.status_code} {response.reason}"
                )
                if raw_response:
                    return response
                # Check for redirect loop or HTML response
                content_type = response.headers.get("Content-Type", "")
                if response.status_code in (301, 302, 303, 307, 308):
                    logger.warning(
                        f"Received redirect ({response.status_code}) to "
                        f"{response.headers.get('Location')}"
                    )
                    last_exception = NetworkError(
                        f"Redirected to {response.headers.get('Location')}", url=url
                    )
                    continue
                if not content_type.startswith("application/json"):
                    logger.warning(f"Non-JSON response received: {content_type}")
                    logger.debug(f"Response text: {response.text[:500]}")
                    last_exception = NetworkError(
                        f"Non-JSON response received: {content_type}", url=url
                    )
                    continue
                # Try to parse JSON and handle as usual
                return self._handle_response(response, url)
            except requests.exceptions.TooManyRedirects as e:
                msg = (
                    f"Redirect loop detected when accessing {url}. "
                    f"This may indicate a server configuration issue. "
                    f"Please check if the API endpoint is correct or try again later."
                )
                logger.error(msg)
                logger.exception(e)
                last_exception = NetworkError(msg, url=url)
                continue
            except Exception as e:
                logger.error(f"[{correlation_id}] Exception: {e}")
                logger.exception(e)
                last_exception = e
                continue
        # If all attempts fail, raise the last exception
        if last_exception:
            raise last_exception
        raise NetworkError(
            f"Failed to get a valid response from {url} after trying multiple "
            f"User-Agents.",
            url=url,
        )

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a GET request to the Athena API.

        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return self.request("GET", path, params=params, raw_response=raw_response)

    def post(
        self,
        path: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a POST request to the Athena API.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return self.request(
            "POST", path, data=data, params=params, raw_response=raw_response
        )

    def close(self) -> None:
        """Closes the underlying HTTP session."""
        logger.info("Closing HTTP session.")
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
