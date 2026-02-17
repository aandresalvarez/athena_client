"""
HTTP client implementation for Athena API.

This module provides HTTP clients for making requests to the Athena API,
with features like retry, backoff, and timeout handling.
"""

import logging
import random
import threading
import time
from typing import Any, Dict, Optional, Tuple, TypeVar, Union
from urllib.parse import ParseResult, urlparse

import orjson
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
from .utils.user_agents import USER_AGENTS, get_default_headers

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
        self._athena_session_initialized = self._has_athena_session_cookie()
        self._athena_session_seed_lock = threading.Lock()

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

    # Use centralized User-Agents (kept as class attribute for easier testing/mocking)
    _USER_AGENTS = USER_AGENTS

    def _setup_default_headers(self, user_agent_idx: int = 0) -> Dict[str, str]:
        """Set up default headers for all requests, with optional User-Agent index."""
        return get_default_headers(user_agent_idx=user_agent_idx)

    def _parse_base_url(self) -> ParseResult:
        """Parse base URL, tolerating schemeless values.

        If a URL is provided without a scheme (e.g. ``athena.ohdsi.org/api/v1``),
        this normalizes it to https for host matching and seed URL generation.
        """
        parsed = urlparse(self.base_url)
        if parsed.scheme and parsed.netloc:
            return parsed

        return urlparse(f"https://{self.base_url}")

    def _is_athena_host(self) -> bool:
        """Return True when the current base URL points to athena.ohdsi.org."""
        parsed = self._parse_base_url()
        hostname = parsed.hostname or ""
        return hostname == "athena.ohdsi.org" or hostname.endswith(".athena.ohdsi.org")

    def _has_athena_session_cookie(self) -> bool:
        """Return True when the client session already has an athena_session cookie."""
        return any(cookie.name == "athena_session" for cookie in self.session.cookies)

    def _search_terms_url(self) -> str:
        """Return the public web page URL used to initialize session cookies."""
        if self._is_athena_host():
            parsed = self._parse_base_url()
            return f"{parsed.scheme or 'https'}://{parsed.hostname}/search-terms/terms"

        return self._build_url("/search-terms/terms")

    def _seed_athena_session(self) -> bool:
        """
        Hit the public web page to establish an athena_session cookie.
        """
        if self._athena_session_initialized or not self._is_athena_host():
            return self._athena_session_initialized

        with self._athena_session_seed_lock:
            if self._athena_session_initialized or not self._is_athena_host():
                return self._athena_session_initialized

            search_url = self._search_terms_url()
            try:
                response = self.session.get(
                    search_url,
                    headers=self._setup_default_headers(),
                    timeout=self.timeout,
                )
                logger.debug(
                    "Session bootstrap request to %s returned %s",
                    search_url,
                    response.status_code,
                )
                if response.status_code == 200 and self._has_athena_session_cookie():
                    self._athena_session_initialized = True
            except requests.RequestException as e:
                logger.warning("Failed to seed Athena session: %s", e)

        return self._athena_session_initialized

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
        Build the full URL for an API endpoint.
        """
        # Ensure base_url doesn't end with / and path doesn't start with /
        base = self.base_url.rstrip("/")
        path = path.lstrip("/")

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
        """
        # Log raw response for debugging
        raw_response_text = response.text
        logger.debug(f"Raw response text from {url}: {raw_response_text[:1000]}...")

        try:
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")
                redirect_note = f" to {location}" if location else ""
                msg = (
                    f"Unexpected redirect ({response.status_code}){redirect_note} "
                    f"when accessing {url}. Check the API base URL."
                )
                logger.error(msg)
                raise NetworkError(msg, url=url)

            response.raise_for_status()

            # Attempt to parse JSON using orjson for better performance
            data = orjson.loads(response.content)
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

        except (orjson.JSONDecodeError, TypeError, ValueError) as e:
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
        timeout: Optional[int] = None,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make an HTTP request to the Athena API with enhanced retry and throttling.
        Tries multiple User-Agents and browser-like headers if the server returns
        a redirect loop or non-JSON response.
        """
        url = self._build_url(path)
        body_bytes = b""
        if data is not None:
            body_bytes = orjson.dumps(data)
        auth_headers = build_headers(method, url, body_bytes)
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

            # Compose headers for this specific attempt without modifying session state
            headers = self._setup_default_headers(user_agent_idx=agent_idx)
            headers.update(auth_headers)
            # Only add Content-Type for requests with body (POST/PUT)
            if data is not None:
                headers["Content-Type"] = "application/json"

            try:
                # Use provided timeout or fall back to instance timeout
                request_timeout = timeout if timeout is not None else self.timeout
                response = self.session.request(
                    method=method,
                    url=url,
                    params=normalized_params,
                    data=body_bytes if data is not None else None,
                    headers=headers,
                    timeout=request_timeout,
                )
                logger.debug(
                    f"[{correlation_id}] {response.status_code} {response.reason}"
                )
                if raw_response:
                    return response
                # Check for redirect loop or HTML response
                content_type = response.headers.get("Content-Type", "")
                is_json = content_type.startswith("application/json")
                is_html = content_type.startswith("text/html")
                if response.status_code in (301, 302, 303, 307, 308):
                    logger.warning(
                        f"Received redirect ({response.status_code}) to "
                        f"{response.headers.get('Location')}"
                    )
                    return self._handle_response(response, url)
                if response.status_code == 403 and is_html:
                    if self._is_athena_host() and not self._athena_session_initialized:
                        self._seed_athena_session()
                    logger.warning(f"HTML 403 received: {content_type}")
                    logger.debug(f"Response text: {response.text[:500]}")
                    last_exception = NetworkError(
                        f"Non-JSON response received: {content_type}", url=url
                    )
                    continue
                if not is_json:
                    return self._handle_response(response, url)
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
            except AthenaError:
                raise
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
        timeout: Optional[int] = None,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a GET request to the Athena API.

        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object
            timeout: Optional timeout override for this request

        Returns:
            Parsed JSON response or raw Response object
        """
        if timeout is None:
            return self.request("GET", path, params=params, raw_response=raw_response)
        return self.request(
            "GET",
            path,
            params=params,
            raw_response=raw_response,
            timeout=timeout,
        )

    def post(
        self,
        path: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
        timeout: Optional[int] = None,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a POST request to the Athena API.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            raw_response: Whether to return the raw response object
            timeout: Optional timeout override for this request

        Returns:
            Parsed JSON response or raw Response object
        """
        if timeout is None:
            return self.request(
                "POST", path, data=data, params=params, raw_response=raw_response
            )
        return self.request(
            "POST",
            path,
            data=data,
            params=params,
            raw_response=raw_response,
            timeout=timeout,
        )

    def close(self) -> None:
        """Closes the underlying HTTP session."""
        logger.info("Closing HTTP session.")
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
