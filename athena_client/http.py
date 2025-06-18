"""
HTTP client implementation for Athena API.

This module provides HTTP clients for making requests to the Athena API,
with features like retry, backoff, and timeout handling.
"""
import json
import logging
from typing import Any, Dict, Optional, Tuple, TypeVar, Union, overload
from urllib.parse import urljoin

import backoff
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import build_headers
from .exceptions import AthenaError, ClientError, NetworkError, ServerError
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
        
        # Create session with retry configuration
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """
        Create and configure a requests Session with retry logic.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.
        
        Args:
            path: API endpoint path
            
        Returns:
            Full URL
        """
        return urljoin(self.base_url, path)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: HTTP response from requests
            
        Returns:
            Parsed JSON response
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            else:
                raise
        except requests.exceptions.JSONDecodeError as e:
            raise AthenaError(f"Invalid JSON response: {e}") from e
    
    @overload
    def request(
        self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, raw_response: bool = False,
    ) -> Dict[str, Any]: ...
    
    @overload
    def request(
        self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, raw_response: bool = True,
    ) -> requests.Response: ...
    
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        max_tries=3,
        factor=0.3,
    )
    def request(
        self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make an HTTP request to the Athena API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        url = self._build_url(path)
        body_bytes = b""
        
        # Convert data to JSON bytes if provided
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")
            
        # Build authentication headers
        headers = build_headers(method, url, body_bytes)
        
        # Add Content-Type header if sending data
        if data is not None:
            headers["Content-Type"] = "application/json"
        
        # Generate a correlation ID for logging
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(f"[{correlation_id}] {method} {url}")
            
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=body_bytes if data is not None else None,
                headers=headers,
                timeout=self.timeout,
            )
            
            logger.debug(
                f"[{correlation_id}] {response.status_code} {response.reason}"
            )
                
            if raw_response:
                return response
                
            return self._handle_response(response)
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"[{correlation_id}] Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e
    
    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None, raw_response: bool = False
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
        self, path: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False
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
        return self.request("POST", path, data=data, params=params, raw_response=raw_response)
