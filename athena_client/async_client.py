"""
Async HTTP client for the Athena API.

This module provides an asynchronous HTTP client for interacting with the Athena API.
It uses httpx for HTTP requests and provides automatic retry logic, rate limiting,
and error handling.
"""

import logging
from typing import Any, Dict, Optional, Union, cast

import orjson

try:
    import httpx
except ImportError as err:
    raise AttributeError(
        "httpx is required for the async client. Install with 'pip install httpx'"
    ) from err

try:
    import backoff
except ImportError as err:
    raise ImportError(
        "backoff is required for the async client. Install with 'pip install backoff'"
    ) from err

from .auth import build_headers
from .concept_explorer import create_concept_explorer
from .concept_set import ConceptSetGenerator
from .db.base import DatabaseConnector
from .exceptions import AthenaError, ClientError, NetworkError, ServerError
from .models import (
    ConceptDetails,
    ConceptRelationsGraph,
    ConceptRelationship,
    ConceptSearchResponse,
)
from .search_result import SearchResult
from .settings import get_settings
from .utils.user_agents import USER_AGENTS, get_default_headers

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """
    Asynchronous HTTP client for making requests to the Athena API.

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
        db_connector: Optional[DatabaseConnector] = None,
    ) -> None:
        """
        Initialize the async HTTP client with configuration.

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

        # Create httpx client
        self.client = httpx.AsyncClient(timeout=self.timeout)

    # Use centralized User-Agents (kept as class attribute for easier testing/mocking)
    _USER_AGENTS = USER_AGENTS

    def _setup_default_headers(self, user_agent_idx: int = 0) -> Dict[str, str]:
        """Set up default headers for all requests, with optional User-Agent index."""
        return get_default_headers(user_agent_idx=user_agent_idx)

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    def __del__(self) -> None:
        """Warning if the client was not properly closed."""
        try:
            if hasattr(self, "client") and not self.client.is_closed:
                logger.warning(
                    "AsyncHttpClient was not closed. "
                    "Use 'async with' or call 'await client.aclose()' to avoid leaking resources."
                )
        except Exception:
            # Destructors should not raise exceptions
            pass

    async def __aenter__(self) -> "AsyncHttpClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    def _compose_request_headers(
        self, auth_headers: Dict[str, str], user_agent_idx: int, has_data: bool
    ) -> Dict[str, str]:
        """Compose final request headers from defaults and auth without duplication."""
        # Get base headers for the specific User-Agent index without modifying state
        headers = self._setup_default_headers(user_agent_idx=user_agent_idx)
        headers.update(auth_headers)
        # Only add Content-Type for requests with body (POST/PUT)
        if has_data:
            headers["Content-Type"] = "application/json"
        return headers

    def _build_url(self, path: str) -> str:
        """
        Build full URL for API request.
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

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response from httpx

        Returns:
            Parsed JSON response
        """
        try:
            if response.status_code in (301, 302, 303, 307, 308):
                location = response.headers.get("Location")
                redirect_note = f" to {location}" if location else ""
                request_url = (
                    str(response.request.url) if response.request is not None else ""
                )
                msg = (
                    f"Unexpected redirect ({response.status_code}){redirect_note} "
                    f"when accessing {request_url}. Check the API base URL."
                )
                logger.error(msg)
                raise NetworkError(msg, url=request_url)

            response.raise_for_status()
            # Use orjson for better performance
            return orjson.loads(response.content)
        except httpx.HTTPStatusError as e:
            if 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            else:
                raise
        except httpx.DecodingError as e:
            raise AthenaError(f"Invalid JSON response: {e}") from e

    @backoff.on_exception(
        backoff.expo,
        (httpx.TimeoutException, httpx.ConnectError),
        max_tries=3,
        factor=0.3,
    )
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
        timeout: Optional[int] = None,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make an HTTP request to the Athena API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            raw_response: Whether to return the raw response object
            timeout: Optional timeout override for this request

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
            body_bytes = orjson.dumps(data)

        # Build authentication headers
        auth_headers = build_headers(method, url, body_bytes)
        headers = self._compose_request_headers(auth_headers, 0, data is not None)

        # Generate a correlation ID for logging
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(f"[{correlation_id}] {method} {url}")

        last_exception: Optional[Exception] = None
        # Try with multiple browser-like User-Agents if needed
        for agent_idx, agent in enumerate(self._USER_AGENTS):
            if agent_idx > 0:
                logger.info(f"Retrying with fallback User-Agent: {agent}")

            headers = self._compose_request_headers(
                auth_headers,
                agent_idx,
                data is not None,
            )
            try:
                request_timeout = timeout if timeout is not None else self.timeout
                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    content=body_bytes if data is not None else None,
                    headers=headers,
                    timeout=request_timeout,
                )

                logger.debug(
                    (
                        f"[{correlation_id}] {response.status_code} "
                        f"{response.reason_phrase}"
                    )
                )

                if raw_response:
                    return response

                # Validate content type is JSON
                content_type = response.headers.get("Content-Type", "")
                is_json = content_type.startswith("application/json")
                is_html = content_type.startswith("text/html")
                if response.status_code == 403 and is_html:
                    logger.warning(
                        (
                            "Non-JSON response received: "
                            f"{content_type}; trying next User-Agent"
                        )
                    )
                    last_exception = NetworkError(
                        f"Non-JSON response received: {content_type}",
                    )
                    continue
                if not is_json:
                    return await self._handle_response(response)

                return await self._handle_response(response)

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                logger.warning(f"[{correlation_id}] Network error: {e}")
                # Do not retry with different User-Agent for network issues;
                # raise immediately
                raise NetworkError(f"Network error: {e}") from e

        # Exhausted User-Agents
        if last_exception:
            raise last_exception
        raise NetworkError(
            (
                "Failed to get a valid response from "
                f"{url} after trying multiple User-Agents."
            ),
        )

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
        timeout: Optional[int] = None,
    ) -> Union[Dict[str, Any], httpx.Response]:
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
            return await self.request(
                "GET", path, params=params, raw_response=raw_response
            )
        return await self.request(
            "GET",
            path,
            params=params,
            raw_response=raw_response,
            timeout=timeout,
        )

    async def post(
        self,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
        timeout: Optional[int] = None,
    ) -> Union[Dict[str, Any], httpx.Response]:
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
            return await self.request(
                "POST", path, data=data, params=params, raw_response=raw_response
            )
        return await self.request(
            "POST",
            path,
            data=data,
            params=params,
            raw_response=raw_response,
            timeout=timeout,
        )


class AthenaAsyncClient:
    """
    Asynchronous client for the Athena API.

    This class provides asynchronous access to all Athena API endpoints
    with minimal abstraction, returning parsed Pydantic models.
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
        db_connector: Optional[DatabaseConnector] = None,
    ) -> None:
        """
        Initialize the async Athena client with configuration.

        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
            db_connector: Optional database connector for local OMOP validation
        """
        self.http = AsyncHttpClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
        self.db_connector = db_connector

    def set_database_connector(self, connector: DatabaseConnector) -> None:
        """Set the database connector for this client."""

        self.db_connector = connector

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self.http.aclose()

    def __del__(self) -> None:
        """Warning if the client was not properly closed."""
        try:
            if hasattr(self, "http") and hasattr(self.http, "client") and not self.http.client.is_closed:
                logger.warning(
                    "AthenaAsyncClient was not closed. "
                    "Use 'async with' or call 'await client.aclose()' to avoid leaking resources."
                )
        except Exception:
            # Destructors should not raise exceptions
            pass

    async def __aenter__(self) -> "AthenaAsyncClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    async def search_concepts(
        self,
        query: str = "",
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search for concepts in the Athena vocabulary.

        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status
            timeout: Optional request timeout

        Returns:
            Raw API response data
        """
        # Convert page to start parameter that the API expects
        start = page * page_size

        params: Dict[str, Any] = {"pageSize": page_size, "start": start}

        # Add query if provided
        if query:
            params["query"] = query

        # Add filters if provided
        if exact:
            params["exact"] = exact
        if fuzzy:
            params["fuzzy"] = str(fuzzy).lower()
        if wildcard:
            params["wildcard"] = wildcard
        if domain:
            params["domain"] = domain
        if vocabulary:
            params["vocabulary"] = vocabulary
        if standard_concept:
            params["standardConcept"] = standard_concept

        # If boosts provided, use debug endpoint and include boosts in request
        if boosts or debug:
            response = await self.http.post(
                "/concepts",
                data={"boosts": boosts} if boosts else {},
                params=params,
                timeout=timeout,
            )
            return cast(Dict[str, Any], response)

        # Otherwise use standard GET endpoint
        response = await self.http.get("/concepts", params=params, timeout=timeout)
        return cast(Dict[str, Any], response)

    async def search(
        self,
        query: str = "",
        size: int = 20,
        page: int = 0,
        **kwargs: Any,
    ) -> SearchResult:
        """
        Search for concepts with a SearchResult wrapper.

        Args:
            query: The search query string
            size: Number of results per page
            page: Page number (0-indexed)
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with convenient access methods
        """
        from .utils import estimate_query_size, get_operation_timeout

        # Calculate appropriate timeout based on query complexity
        estimated_size = estimate_query_size(query)
        operation_timeout = get_operation_timeout("search", estimated_size)

        # Convert size to pageSize for the API
        search_kwargs: Dict[str, Any] = dict(kwargs)
        search_kwargs["page_size"] = size
        search_kwargs["page"] = page

        # Use dynamic timeout if not explicitly provided in kwargs
        if "timeout" not in search_kwargs:
            search_kwargs["timeout"] = operation_timeout

        response_data = await self.search_concepts(query=query, **search_kwargs)
        response = ConceptSearchResponse.model_validate(response_data)
        return SearchResult(response, self, query=query, **kwargs)

    async def details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.

        This is an alias for get_concept_details for compatibility.

        Args:
            concept_id: The concept ID to get details for

        Returns:
            ConceptDetails object
        """
        return await self.get_concept_details(concept_id)

    async def relationships(
        self,
        concept_id: int,
        only_standard: bool = False,
        relationship_id: Optional[str] = None,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.

        This is an alias for get_concept_relationships for compatibility.

        Args:
            concept_id: The concept ID to get relationships for
            only_standard: Only include standard concepts
            relationship_id: Filter by relationship type

        Returns:
            ConceptRelationship object
        """
        return await self.get_concept_relationships(
            concept_id, relationship_id=relationship_id, only_standard=only_standard
        )

    async def get_concept_details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.

        Args:
            concept_id: The concept ID to get details for

        Returns:
            ConceptDetails object
        """
        from .utils import get_operation_timeout
        timeout = get_operation_timeout("details", 1)
        response = await self.http.get(f"/concepts/{concept_id}", timeout=timeout)
        data = cast(Dict[str, Any], response)
        return ConceptDetails.model_validate(data)

    async def get_concept_relationships(
        self,
        concept_id: int,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.

        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts

        Returns:
            ConceptRelationship object
        """
        params: Dict[str, Any] = {}

        if relationship_id:
            params["relationshipId"] = relationship_id
        if only_standard:
            params["standardConcepts"] = "true"

        from .utils import get_operation_timeout
        timeout = get_operation_timeout("relationships", 1)
        response = await self.http.get(
            f"/concepts/{concept_id}/relationships", params=params, timeout=timeout
        )
        data = cast(Dict[str, Any], response)
        return ConceptRelationship.model_validate(data)

    async def get_concept_graph(
        self,
        concept_id: int,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.

        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph

        Returns:
            ConceptRelationsGraph object
        """
        params = {"depth": depth, "zoomLevel": zoom_level}
        from .utils import get_operation_timeout
        # Use depth and zoom to estimate complexity
        estimated_complexity = depth * zoom_level * 5
        timeout = get_operation_timeout("graph", estimated_complexity)
        response = await self.http.get(
            f"/concepts/{concept_id}/relations", params=params, timeout=timeout
        )
        data = cast(Dict[str, Any], response)
        return ConceptRelationsGraph.model_validate(data)

    async def generate_concept_set(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate a validated concept set from a search query."""

        if not self.db_connector:
            raise RuntimeError("A database connector has not been configured.")

        explorer = create_concept_explorer(self)
        generator = ConceptSetGenerator(explorer=explorer, db=self.db_connector)

        return await generator.create_from_query(query, **kwargs)
