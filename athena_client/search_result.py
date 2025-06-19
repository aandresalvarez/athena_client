"""
Search result wrapper for Athena API responses.

This module provides a wrapper around search results that provides
convenient access to the data in various formats.
"""

from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

import pandas as pd

from .models import Concept, ConceptSearchResponse

if TYPE_CHECKING:
    pass


class SearchResult:
    """Wrapper for search results that provides convenient access methods."""

    def __init__(self, response: ConceptSearchResponse, client: Any) -> None:
        """Initialize the search result wrapper.

        Args:
            response: The search response from the API
            client: The client instance for making additional requests
        """
        self._response = response
        self._client = client

    def all(self) -> List[Concept]:
        """Get all concepts from the current page.

        Returns:
            List of Concept objects
        """
        return self._response.content

    def top(self, n: int) -> List[Concept]:
        """Get the top N concepts from the current page.

        Args:
            n: Number of concepts to return

        Returns:
            List of Concept objects
        """
        return self._response.content[:n]

    def to_list(self) -> List[Dict[str, Any]]:
        """Convert results to a list of dictionaries.

        Returns:
            List of dictionaries representing concepts
        """
        return [concept.model_dump() for concept in self._response.content]

    def to_json(self) -> str:
        """Convert results to JSON string.

        Returns:
            JSON string representation of the results
        """
        return self._response.model_dump_json()

    def to_df(self) -> pd.DataFrame:
        """Convert results to a pandas DataFrame.

        Returns:
            DataFrame containing the concept data
        """
        try:
            data = self.to_list()
            return pd.DataFrame(data)
        except ImportError:
            raise ImportError(
                "pandas is required for DataFrame output. "
                "Install with: pip install 'athena-client[pandas]'"
            ) from None

    def next_page(self) -> Optional["SearchResult"]:
        """Get the next page of results.

        Returns:
            SearchResult for the next page, or None if no more pages
        """
        if self._response.last:
            return None
        current_page = self._response.number
        size = self._response.size
        if current_page is None or size is None:
            return None
        return self._client.search(
            query="",  # This would need to be the original query
            page=current_page + 1,
            size=size,
        )

    def previous_page(self) -> Optional["SearchResult"]:
        """Get the previous page of results.

        Returns:
            SearchResult for the previous page, or None if no previous pages
        """
        if self._response.first:
            return None
        current_page = self._response.number
        size = self._response.size
        if current_page is None or size is None:
            return None
        return self._client.search(
            query="",  # This would need to be the original query
            page=current_page - 1,
            size=size,
        )

    @property
    def total_elements(self) -> int:
        """Get the total number of elements across all pages.

        Returns:
            Total number of elements
        """
        # Try to get from direct field first, then from pageable
        if self._response.totalElements is not None:
            return self._response.totalElements

        # Extract from pageable if available
        pageable = self._response.pageable
        if pageable and "totalElements" in pageable:
            return pageable["totalElements"]

        # Fallback to number of elements in current page
        return len(self._response.content)

    @property
    def total_pages(self) -> int:
        """Get the total number of pages.

        Returns:
            Total number of pages
        """
        # Try to get from direct field first, then calculate from pageable
        if self._response.totalPages is not None:
            return self._response.totalPages

        # Calculate from pageable if available
        pageable = self._response.pageable
        if pageable and "totalElements" in pageable and "pageSize" in pageable:
            total_elements = pageable["totalElements"]
            page_size = pageable["pageSize"]
            return (total_elements + page_size - 1) // page_size

        return 1

    @property
    def current_page(self) -> int:
        """Get the current page number.

        Returns:
            Current page number
        """
        # Try to get from direct field first, then from pageable
        if self._response.number is not None:
            return self._response.number

        # Extract from pageable if available
        pageable = self._response.pageable
        if pageable and "pageNumber" in pageable:
            return pageable["pageNumber"]

        return 0

    @property
    def page_size(self) -> int:
        """Get the page size.

        Returns:
            Page size
        """
        # Try to get from direct field first, then from pageable
        if self._response.size is not None:
            return self._response.size

        # Extract from pageable if available
        pageable = self._response.pageable
        if pageable and "pageSize" in pageable:
            return pageable["pageSize"]

        return len(self._response.content)

    @property
    def facets(self) -> Optional[Dict[str, Any]]:
        """Get search facets if available.

        Returns:
            Search facets dictionary or None
        """
        return self._response.facets

    def __len__(self) -> int:
        """Get the number of concepts in the current page.

        Returns:
            Number of concepts
        """
        return len(self._response.content)

    def __getitem__(self, index: int) -> Concept:
        """Get a concept by index.

        Args:
            index: Index of the concept

        Returns:
            Concept object
        """
        return self._response.content[index]

    def __iter__(self) -> Iterator["Concept"]:
        """Iterate over concepts in the current page.

        Returns:
            Iterator over Concept objects
        """
        return iter(self._response.content)
