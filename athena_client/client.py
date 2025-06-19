"""
Main client for the Athena API.

This module provides the main client class for interacting with the Athena API.
"""

import logging
import time
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from .async_client import AthenaAsyncClient
from .db.base import DatabaseConnector
from .db.sqlalchemy_connector import SQLAlchemyConnector
from .exceptions import APIError, AthenaError
from .http import HttpClient
from .models import (
    ConceptDetails,
    ConceptRelationsGraph,
    ConceptRelationship,
    ConceptSearchResponse,
)
from .query import Q
from .search_result import SearchResult
from .settings import get_settings

logger = logging.getLogger(__name__)


class AthenaClient:
    """Main client for interacting with the Athena API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        enable_throttling: bool = True,
        throttle_delay_range: Tuple[float, float] = (0.1, 0.3),
        db_connector: Optional[DatabaseConnector] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Athena client.

        Args:
            base_url: Base URL for the Athena API
            token: Authentication token
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for network errors
            retry_delay: Delay between retry attempts in seconds
                (overrides backoff_factor)
            enable_throttling: Whether to throttle requests to be respectful
                to the server
            throttle_delay_range: Range of delays for throttling (min, max)
                in seconds
            db_connector: Optional database connector for local OMOP validation
            **kwargs: Additional settings
        """
        s = get_settings()

        # Configure retry settings
        self.max_retries = max_retries or s.ATHENA_MAX_RETRIES
        self.retry_delay = retry_delay
        self.enable_throttling = enable_throttling
        self.throttle_delay_range = throttle_delay_range
        self._db_connector = db_connector

        # Create HTTP client with enhanced configuration
        self.http = HttpClient(
            base_url=base_url or s.ATHENA_BASE_URL,
            token=token or s.ATHENA_TOKEN,
            timeout=timeout or s.ATHENA_TIMEOUT_SECONDS,
            max_retries=self.max_retries,
            enable_throttling=self.enable_throttling,
            throttle_delay_range=self.throttle_delay_range,
            **kwargs,
        )

        logger.info(
            f"Athena client initialized: "
            f"max_retries={self.max_retries}, "
            f"retry_delay={self.retry_delay}, "
            f"throttling={'enabled' if self.enable_throttling else 'disabled'}"
        )

    def set_database_connector(self, connector: DatabaseConnector) -> None:
        """Set the database connector for this client."""

        self._db_connector = connector

    def validate_local_concepts(self, concept_ids: List[int]) -> List[int]:
        """Validate concept IDs against the configured local database."""

        if not self._db_connector:
            raise RuntimeError(
                "A database connector has not been configured. Use "
                "`set_database_connector()` to provide one."
            )

        return self._db_connector.validate_concepts(concept_ids)

    def search(
        self,
        query: Union[str, Q],
        page: int = 0,
        size: int = 20,
        auto_retry: bool = True,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
        show_progress: Optional[bool] = None,
        **kwargs: Any,
    ) -> SearchResult:
        """
        Search for concepts with automatic error handling and recovery.

        Args:
            query: Search query string or Query DSL object
            page: Page number (0-based)
            size: Page size
            auto_retry: Whether to automatically retry on recoverable errors
            max_retries: Override max retries for this call
            retry_delay: Override retry delay for this call
            show_progress: Whether to show progress for large queries
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with concepts

        Note:
            This method includes automatic error handling and recovery.
            Network errors are automatically retried, and API errors provide
            clear, actionable messages without requiring try-catch blocks.
        """

        from .exceptions import RetryFailedError
        from .settings import get_settings
        from .utils import (
            estimate_query_size,
            format_large_query_warning,
            get_operation_timeout,
            progress_context,
        )

        settings = get_settings()

        if isinstance(query, Q):
            query_str = str(query)
        else:
            query_str = query

        # Estimate query size and provide warnings for large queries
        estimated_size = estimate_query_size(query_str)
        warning = format_large_query_warning(query_str, estimated_size)
        if warning:
            print(warning)

        # Use settings default page size if not specified
        if size == 20 and "pageSize" not in kwargs:
            size = settings.ATHENA_DEFAULT_PAGE_SIZE

        # Validate page size
        if size > settings.ATHENA_MAX_PAGE_SIZE:
            raise ValueError(
                f"Page size {size} exceeds maximum allowed size of "
                f"{settings.ATHENA_MAX_PAGE_SIZE}. Please use a smaller page size."
            )

        # Convert page/size to pageSize/start parameters that the API expects
        page_size = size
        start = page * size  # Calculate start offset

        params = {
            "query": query_str,
            "pageSize": page_size,
            "start": start,
            **kwargs,
        }

        # Configure retry settings for this call
        max_attempts = max(
            1,
            max_retries
            if max_retries is not None
            else (self.max_retries if auto_retry else 1),
        )

        # Get appropriate timeout for this operation
        operation_timeout = get_operation_timeout("search", estimated_size)

        # Set up progress tracking if enabled
        progress_kwargs: Optional[Dict[str, Any]] = None
        if show_progress:
            progress_kwargs = {
                "total": estimated_size,
                "description": f"Searching for '{query_str}'",
                "show_progress": show_progress,
                "update_interval": settings.ATHENA_PROGRESS_UPDATE_INTERVAL,
            }

        retry_history: list[Exception] = []
        with progress_context(**progress_kwargs) if progress_kwargs else nullcontext():
            for attempt in range(max_attempts):
                try:
                    # Create a temporary HTTP client with the appropriate timeout
                    temp_http = HttpClient(
                        base_url=self.http.base_url,
                        token=str(self.http.session.headers.get("Authorization", "")),
                        timeout=operation_timeout,
                        max_retries=1,  # We handle retries manually
                        enable_throttling=self.http.enable_throttling,
                        throttle_delay_range=self.http.throttle_delay_range,
                    )

                    response = temp_http.get("/concepts", params=params)

                    # Raise APIError for any error response with errorMessage
                    # and errorCode
                    if (
                        isinstance(response, dict)
                        and response.get("result") is None
                        and "errorMessage" in response
                        and "errorCode" in response
                    ):
                        error_msg = response.get("errorMessage", "Unknown API error")
                        error_code = response.get("errorCode")

                        # Enhanced error messages for large queries
                        if "timeout" in error_msg.lower():
                            raise APIError(
                                f"Search timeout: The query '{query_str}' "
                                f"is taking too long to process. "
                                f"Try:\n"
                                f"• Using more specific search terms\n"
                                f"• Adding domain or vocabulary filters\n"
                                f"• Reducing the page size\n"
                                f"• Breaking the query into smaller parts",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )
                        elif "Page size must not be less than one" in error_msg:
                            raise APIError(
                                f"Invalid page size: {error_msg}. "
                                f"Please use a page size of 1 or greater.",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )
                        elif "Page size must not be greater than" in error_msg:
                            raise APIError(
                                f"Page size too large: {error_msg}. "
                                f"Please reduce the page size to "
                                f"{settings.ATHENA_MAX_PAGE_SIZE} or less.",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )
                        elif "Query must not be blank" in error_msg:
                            raise APIError(
                                f"Empty search query: {error_msg}. "
                                f"Please provide a search term.",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )
                        else:
                            raise APIError(
                                f"Search failed: {error_msg}",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )

                    search_response = ConceptSearchResponse.model_validate(response)
                    return SearchResult(search_response, self)

                except Exception as e:
                    if isinstance(e, APIError):
                        # API errors are not retryable, raise immediately
                        raise

                    # For network errors, retry if we have attempts left
                    if attempt < max_attempts - 1:
                        logger.info(
                            f"Retrying search due to {type(e).__name__} "
                            f"(attempt {attempt + 1}/{max_attempts}): {e}"
                        )
                        if retry_delay is not None:
                            time.sleep(retry_delay)
                        elif self.retry_delay is not None:
                            time.sleep(self.retry_delay)
                        retry_history.append(e)
                        continue
                    else:
                        # Final attempt failed, raise with retry history
                        raise RetryFailedError(
                            f"Search failed after {max_attempts} attempts",
                            retry_history=retry_history,
                            max_attempts=max_attempts,
                            last_error=e,
                        ) from e
            raise RuntimeError("Unreachable code in search")

    def details(self, concept_id: int, auto_retry: bool = True) -> ConceptDetails:
        """
        Get detailed information about a concept with automatic error handling.

        Args:
            concept_id: Concept ID
            auto_retry: Whether to automatically retry on recoverable errors

        Returns:
            ConceptDetails object

        Note:
            This method includes automatic error handling and recovery.
            Network errors are automatically retried, and API errors provide
            clear, actionable messages without requiring try-catch blocks.
        """
        max_attempts = 3 if auto_retry else 1

        for attempt in range(max_attempts):
            try:
                response = self.http.get(f"/concepts/{concept_id}")

                # Check if the response is an error response
                if (
                    isinstance(response, dict)
                    and response.get("result") is None
                    and "errorMessage" in response
                ):
                    error_msg = response.get("errorMessage", "Unknown API error")
                    error_code = response.get("errorCode")

                    # Provide more specific error messages for concept details
                    if "Unable to find" in error_msg and "ConceptV5" in error_msg:
                        raise APIError(
                            f"Concept not found: Concept ID {concept_id} "
                            f"does not exist in the database. "
                            f"Please verify the concept ID is correct.",
                            api_error_code=error_code,
                            api_message=error_msg,
                        )
                    else:
                        raise APIError(
                            f"Failed to get concept details: {error_msg}",
                            api_error_code=error_code,
                            api_message=error_msg,
                        )

                return ConceptDetails.model_validate(response)

            except Exception as e:
                if isinstance(e, APIError):
                    # API errors are not retryable, raise immediately
                    raise
                elif attempt < max_attempts - 1:
                    # For other errors, retry if we have attempts left
                    logger.info(
                        f"Retrying concept details due to error "
                        f"(attempt {attempt + 1}/{max_attempts}): {e}"
                    )
                    continue
                else:
                    # Final attempt failed, raise with enhanced message
                    raise AthenaError(
                        f"Failed to get concept details after {max_attempts} attempts. "
                        f"Last error: {e}",
                        error_code="RETRY_FAILED",
                        troubleshooting=(
                            "• Check your internet connection\n"
                            "• Try again in a few moments\n"
                            "• Contact support if the problem persists"
                        ),
                    ) from e
        raise RuntimeError("Unreachable code in details")

    def relationships(
        self, concept_id: int, auto_retry: bool = True
    ) -> ConceptRelationship:
        """
        Get relationships for a concept with automatic error handling.

        Args:
            concept_id: Concept ID
            auto_retry: Whether to automatically retry on recoverable errors

        Returns:
            ConceptRelationship object

        Note:
            This method includes automatic error handling and recovery.
            Network errors are automatically retried, and API errors provide
            clear, actionable messages without requiring try-catch blocks.
        """
        max_attempts = 3 if auto_retry else 1

        for attempt in range(max_attempts):
            try:
                response = self.http.get(f"/concepts/{concept_id}/relationships")

                # Check if the response is an error response
                if (
                    isinstance(response, dict)
                    and response.get("result") is None
                    and "errorMessage" in response
                ):
                    error_msg = response.get("errorMessage", "Unknown API error")
                    error_code = response.get("errorCode")

                    # Provide more specific error messages for relationships
                    if "Unable to find" in error_msg and "ConceptV5" in error_msg:
                        raise APIError(
                            f"Concept not found: Concept ID {concept_id} "
                            f"does not exist in the database. "
                            f"Please verify the concept ID is correct.",
                            api_error_code=error_code,
                            api_message=error_msg,
                        )
                    else:
                        raise APIError(
                            f"Failed to get relationships: {error_msg}",
                            api_error_code=error_code,
                            api_message=error_msg,
                        )

                return ConceptRelationship.model_validate(response)

            except Exception as e:
                if isinstance(e, APIError):
                    # API errors are not retryable, raise immediately
                    raise
                elif attempt < max_attempts - 1:
                    # For other errors, retry if we have attempts left
                    logger.info(
                        f"Retrying relationships due to error "
                        f"(attempt {attempt + 1}/{max_attempts}): {e}"
                    )
                    continue
                else:
                    # Final attempt failed, raise with enhanced message
                    raise AthenaError(
                        f"Failed to get relationships after {max_attempts} attempts. "
                        f"Last error: {e}",
                        error_code="RETRY_FAILED",
                        troubleshooting=(
                            "• Check your internet connection\n"
                            "• Try again in a few moments\n"
                            "• Contact support if the problem persists"
                        ),
                    ) from e
        raise RuntimeError("Unreachable code in relationships")

    def graph(
        self,
        concept_id: int,
        depth: int = 2,
        zoom_level: int = 2,
        auto_retry: bool = True,
        show_progress: Optional[bool] = None,
        **kwargs: Any,
    ) -> ConceptRelationsGraph:
        """
        Get concept relationship graph with automatic error handling.

        Args:
            concept_id: Concept ID
            depth: Graph depth
            zoom_level: Zoom level
            auto_retry: Whether to automatically retry on recoverable errors
            show_progress: Whether to show progress for large graph operations
            **kwargs: Additional parameters

        Returns:
            ConceptRelationsGraph object

        Note:
            This method includes automatic error handling and recovery.
            Network errors are automatically retried, and API errors provide
            clear, actionable messages without requiring try-catch blocks.
        """
        from .settings import get_settings
        from .utils import get_operation_timeout, progress_context

        settings = get_settings()

        # Estimate graph complexity based on depth and zoom level
        estimated_complexity = depth * zoom_level * 100  # Rough estimate

        # Provide warning for complex graphs
        if depth > 3 or zoom_level > 3:
            print(f"⚠️  Complex graph request: depth={depth}, zoom_level={zoom_level}")
            print(
                "💡 This may take several minutes to complete. "
                "Consider reducing depth or zoom level."
            )

        params = {
            "depth": depth,
            "zoomLevel": zoom_level,
            **kwargs,
        }

        max_attempts = 3 if auto_retry else 1

        # Get appropriate timeout for graph operations
        operation_timeout = get_operation_timeout("graph", estimated_complexity)

        # Set up progress tracking if enabled
        progress_kwargs: Optional[Dict[str, Any]] = None
        if show_progress:
            progress_kwargs = {
                "total": estimated_complexity,
                "description": (
                    f"Building graph for concept {concept_id} "
                    f"(depth={depth}, zoom={zoom_level})"
                ),
                "show_progress": show_progress,
                "update_interval": settings.ATHENA_PROGRESS_UPDATE_INTERVAL,
            }

        with progress_context(**progress_kwargs) if progress_kwargs else nullcontext():
            for attempt in range(max_attempts):
                try:
                    # Create a temporary HTTP client with the appropriate timeout
                    temp_http = HttpClient(
                        base_url=self.http.base_url,
                        token=str(self.http.session.headers.get("Authorization", "")),
                        timeout=operation_timeout,
                        max_retries=1,  # We handle retries manually
                        enable_throttling=self.http.enable_throttling,
                        throttle_delay_range=self.http.throttle_delay_range,
                    )

                    response = temp_http.get(
                        f"/concepts/{concept_id}/relations", params=params
                    )

                    # Check if the response is an error response
                    if (
                        isinstance(response, dict)
                        and response.get("result") is None
                        and "errorMessage" in response
                    ):
                        error_msg = response.get("errorMessage", "Unknown API error")
                        error_code = response.get("errorCode")

                        # Enhanced error messages for graph operations
                        if "timeout" in error_msg.lower():
                            raise APIError(
                                f"Graph timeout: The graph for concept {concept_id} "
                                f"is too complex. "
                                f"Try:\n"
                                f"• Reducing the depth (currently {depth})\n"
                                f"• Reducing the zoom level (currently {zoom_level})\n"
                                f"• Using a simpler concept as the starting point\n"
                                f"• Breaking the request into smaller parts",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )
                        elif "Unable to find" in error_msg and "ConceptV5" in error_msg:
                            raise APIError(
                                f"Concept not found: Concept ID {concept_id} "
                                f"does not exist in the database. "
                                f"Please verify the concept ID is correct.",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )
                        else:
                            raise APIError(
                                f"Failed to get concept graph: {error_msg}",
                                api_error_code=error_code,
                                api_message=error_msg,
                            )

                    return ConceptRelationsGraph.model_validate(response)

                except Exception as e:
                    if isinstance(e, APIError):
                        # API errors are not retryable, raise immediately
                        raise
                    elif attempt < max_attempts - 1:
                        # For other errors, retry if we have attempts left
                        logger.info(
                            f"Retrying graph due to error "
                            f"(attempt {attempt + 1}/{max_attempts}): {e}"
                        )
                        continue
                    else:
                        # Final attempt failed, raise with enhanced message
                        raise AthenaError(
                            f"Failed to get concept graph after {max_attempts} "
                            f"attempts. "
                            f"Last error: {e}",
                            error_code="RETRY_FAILED",
                            troubleshooting=(
                                "• Check your internet connection\n"
                                "• Try again in a few moments\n"
                                "• Consider reducing graph depth or zoom level\n"
                                "• Contact support if the problem persists"
                            ),
                        ) from e
            raise RuntimeError("Unreachable code in graph")

    def summary(
        self,
        concept_id: int,
        include_relationships: bool = True,
        include_graph: bool = True,
    ) -> Dict[str, Any]:
        """Get a comprehensive summary of a concept.

        Args:
            concept_id: Concept ID
            include_relationships: Whether to include relationships
            include_graph: Whether to include graph data

        Returns:
            Dictionary containing concept summary

        Raises:
            AthenaError: If any request fails
        """
        summary = {}

        # Get basic details
        try:
            details = self.details(concept_id)
            summary["details"] = details.model_dump()
        except Exception as e:
            summary["details"] = {"error": str(e)}

        # Get relationships if requested
        if include_relationships:
            try:
                relationships = self.relationships(concept_id)
                summary["relationships"] = relationships.model_dump()
            except Exception as e:
                summary["relationships"] = {"error": str(e)}

        # Get graph if requested
        if include_graph:
            try:
                graph = self.graph(concept_id)
                summary["graph"] = graph.model_dump()
            except Exception as e:
                summary["graph"] = {"error": str(e)}

        return summary

    async def generate_concept_set(
        self,
        query: str,
        db_connection_string: str,
        strategy: str = "fallback",
        include_descendants: bool = True,
        confidence_threshold: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate a validated concept set using the async client."""

        async_client = AthenaAsyncClient(
            base_url=self.http.base_url,
            token=str(self.http.session.headers.get("Authorization", "")),
        )

        db_connector = SQLAlchemyConnector.from_connection_string(db_connection_string)
        async_client.set_database_connector(db_connector)

        return await async_client.generate_concept_set(
            query,
            strategy=strategy,
            include_descendants=include_descendants,
            confidence_threshold=confidence_threshold,
            **kwargs,
        )


class Athena(AthenaClient):
    """Alias for AthenaClient for backward compatibility."""

    pass


class nullcontext:
    """Context manager that does nothing."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        return False
