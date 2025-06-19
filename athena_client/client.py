"""
Main client for the Athena API.

This module provides the main client class for interacting with the Athena API.
"""

import logging
from typing import Any, Dict, Optional, Tuple, Union

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
            **kwargs: Additional settings
        """
        s = get_settings()

        # Configure retry settings
        self.max_retries = max_retries or s.ATHENA_MAX_RETRIES
        self.retry_delay = retry_delay
        self.enable_throttling = enable_throttling
        self.throttle_delay_range = throttle_delay_range

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

    def search(
        self,
        query: Union[str, Q],
        page: int = 0,
        size: int = 20,
        auto_retry: bool = True,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
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
            **kwargs: Additional search parameters

        Returns:
            SearchResult object with concepts

        Note:
            This method includes automatic error handling and recovery.
            Network errors are automatically retried, and API errors provide
            clear, actionable messages without requiring try-catch blocks.
        """
        import time

        from .exceptions import RetryFailedError

        if isinstance(query, Q):
            query_str = str(query)
        else:
            query_str = query

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
        retry_delay_seconds = (
            retry_delay if retry_delay is not None else self.retry_delay
        )

        # Track retry history for detailed error reporting
        retry_history = []

        for attempt in range(max_attempts):
            try:
                response = self.http.get("/concepts", params=params)

                # Raise APIError for any error response with errorMessage and errorCode
                if (
                    isinstance(response, dict)
                    and response.get("result") is None
                    and "errorMessage" in response
                    and "errorCode" in response
                ):
                    error_msg = response.get("errorMessage", "Unknown API error")
                    error_code = response.get("errorCode")
                    raise APIError(
                        f"Search failed: {error_msg}",
                        api_error_code=error_code,
                        api_message=error_msg,
                    )

                # Existing special cases (now redundant, but kept for clarity)
                if (
                    isinstance(response, dict)
                    and response.get("result") is None
                    and "errorMessage" in response
                ):
                    error_msg = response.get("errorMessage", "Unknown API error")
                    error_code = response.get("errorCode")

                    if "Page size must not be less than one" in error_msg:
                        raise APIError(
                            f"Invalid page size: {error_msg}. "
                            f"Please use a page size of 1 or greater.",
                            api_error_code=error_code,
                            api_message=error_msg,
                        )
                    elif "Page size must not be greater than" in error_msg:
                        raise APIError(
                            f"Page size too large: {error_msg}. "
                            f"Please reduce the page size.",
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
                    # For other errors, retry if we have attempts left
                    retry_history.append(e)
                    if retry_delay_seconds is not None:
                        time.sleep(retry_delay_seconds)

                    # Log retry attempt
                    logger.info(
                        f"Retrying search due to {type(e).__name__} "
                        f"(attempt {attempt + 1}/{max_attempts}): {e}"
                    )
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
        **kwargs: Any,
    ) -> ConceptRelationsGraph:
        """
        Get concept relationship graph with automatic error handling.

        Args:
            concept_id: Concept ID
            depth: Graph depth
            zoom_level: Zoom level
            auto_retry: Whether to automatically retry on recoverable errors
            **kwargs: Additional parameters

        Returns:
            ConceptRelationsGraph object

        Note:
            This method includes automatic error handling and recovery.
            Network errors are automatically retried, and API errors provide
            clear, actionable messages without requiring try-catch blocks.
        """
        params = {
            "depth": depth,
            "zoomLevel": zoom_level,
            **kwargs,
        }

        max_attempts = 3 if auto_retry else 1

        for attempt in range(max_attempts):
            try:
                response = self.http.get(
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

                    # Provide more specific error messages for graph
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
                        f"Failed to get concept graph after {max_attempts} attempts. "
                        f"Last error: {e}",
                        error_code="RETRY_FAILED",
                        troubleshooting=(
                            "• Check your internet connection\n"
                            "• Try again in a few moments\n"
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


class Athena(AthenaClient):
    """Alias for AthenaClient for backward compatibility."""

    pass
