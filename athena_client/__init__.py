"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""
from typing import Dict, List, Optional, Union, Any

from .client import AthenaClient
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship


__version__ = "1.0.0"


class Athena:
    """
    Main facade for the Athena API client.
    
    This class provides a simplified interface to the Athena API with six
    intuitive verbs that cover 95% of day-to-day use cases.
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
        Initialize the Athena facade with optional configuration.
        
        Args:
            base_url: The base URL for the Athena API.
            token: Bearer token for authentication.
            client_id: Client ID for HMAC authentication.
            private_key: Private key for HMAC signing.
            timeout: HTTP timeout in seconds.
            max_retries: Maximum number of retry attempts.
            backoff_factor: Exponential backoff factor for retries.
        """
        from .client import AthenaClient
        
        self._client = AthenaClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
    
    def search(
        self,
        query: str,
        *,
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[dict] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> "SearchResult":
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
            SearchResult object containing the search results
        """
        from .search_result import SearchResult
        from .query import Q
        
        # If query is a Q object, extract boosts
        if hasattr(query, "to_boosts"):
            boosts = query.to_boosts()
            query = ""
            
        data = self._client.search_concepts(
            query=query,
            exact=exact,
            fuzzy=fuzzy,
            wildcard=wildcard,
            boosts=boosts,
            debug=debug,
            page_size=page_size,
            page=page,
            domain=domain,
            vocabulary=vocabulary,
            standard_concept=standard_concept,
        )
        
        return SearchResult(data)
    
    def details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.
        
        Args:
            concept_id: The concept ID to get details for
            
        Returns:
            ConceptDetails object
        """
        return self._client.get_concept_details(concept_id)
    
    def relationships(
        self,
        concept_id: int,
        *,
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
        return self._client.get_concept_relationships(
            concept_id=concept_id,
            relationship_id=relationship_id,
            only_standard=only_standard,
        )
    
    def graph(
        self,
        concept_id: int,
        *,
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
        return self._client.get_concept_graph(
            concept_id=concept_id,
            depth=depth,
            zoom_level=zoom_level,
        )
    
    def summary(self, concept_id: int) -> Dict[str, Any]:
        """
        Get a comprehensive summary for a concept.
        
        This aggregates details, relationships, and graph information.
        
        Args:
            concept_id: The concept ID to summarize
            
        Returns:
            Dictionary containing details, relationships, and graph
        """
        details = self.details(concept_id)
        relationships = self.relationships(concept_id)
        graph = self.graph(concept_id)
        
        return {
            "details": details,
            "relationships": relationships,
            "graph": graph,
        }
    
    @staticmethod
    def capabilities() -> Dict[str, Dict]:
        """
        Get machine-readable manifest of all supported verbs.
        
        Returns:
            Dictionary containing capabilities information
        """
        return {
            "search": {
                "endpoint": "/concepts",
                "auth": "anonymous|bearer",
                "outputs": ["models", "list", "dataframe", "json", "yaml", "csv"]
            },
            "details": {
                "endpoint": "/concepts/{id}",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"]
            },
            "relationships": {
                "endpoint": "/concepts/{id}/relationships",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"]
            },
            "graph": {
                "endpoint": "/concepts/{id}/relations",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"]
            },
            "summary": {
                "composed_of": ["details", "relationships", "graph"],
                "outputs": ["dict"]
            }
        }

# Type hints for return annotations
from .search_result import SearchResult
