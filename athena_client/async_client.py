"""
Async HTTP client for the Athena API.

This module provides an asynchronous HTTP client for interacting with the Athena API.
It uses httpx for HTTP requests and provides automatic retry logic, rate limiting,
and error handling.
"""

import json
import logging
from typing import Any, Dict, Optional, Union, cast

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

        # Set up default headers
        self._setup_default_headers()

    def _setup_default_headers(self) -> None:
        """Set up default headers for all requests."""
        # Set default headers similar to the working client
        default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "AthenaOHDSIAPIClient/1.0",
        }

        # Update client headers
        self.client.headers.update(default_headers)

        logger.debug("Default headers set: %s", default_headers)

    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.

        Args:
            path: API endpoint path

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

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response from httpx

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
    ) -> Union[Dict[str, Any], httpx.Response]:
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
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                content=body_bytes if data is not None else None,
                headers=headers,
                timeout=self.timeout,
            )

            logger.debug(
                f"[{correlation_id}] {response.status_code} {response.reason_phrase}"
            )

            if raw_response:
                return response

            return await self._handle_response(response)

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.warning(f"[{correlation_id}] Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make a GET request to the Athena API.

        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return await self.request("GET", path, params=params, raw_response=raw_response)

    async def post(
        self,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
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
        return await self.request(
            "POST", path, data=data, params=params, raw_response=raw_response
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
            )
            return cast(Dict[str, Any], response)

        # Otherwise use standard GET endpoint
        response = await self.http.get("/concepts", params=params)
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
        # Convert size to pageSize for the API
        search_kwargs: Dict[str, Any] = dict(kwargs)
        search_kwargs["page_size"] = size
        search_kwargs["page"] = page

        response_data = await self.search_concepts(query=query, **search_kwargs)
        response = ConceptSearchResponse.model_validate(response_data)
        return SearchResult(response, self)

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
        response = await self.http.get(f"/concepts/{concept_id}")
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

        response = await self.http.get(
            f"/concepts/{concept_id}/relationships", params=params
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
        response = await self.http.get(
            f"/concepts/{concept_id}/relations", params=params
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
