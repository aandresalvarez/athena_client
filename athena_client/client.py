"""
Athena API client implementation.

This module provides the core synchronous client for the Athena API.
"""
from typing import Any, Dict, Optional, cast

from .http import HttpClient
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship


class AthenaClient:
    """
    Core synchronous client for the Athena API.
    
    This class provides direct access to all Athena API endpoints
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
    ) -> None:
        """
        Initialize the Athena client with configuration.
        
        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.http = HttpClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
    
    def search_concepts(
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
        params: Dict[str, Any] = {"pageSize": page_size, "page": page}
        
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
            return cast(Dict[str, Any], self.http.post(
                "/concepts",
                data={"boosts": boosts} if boosts else {},
                params=params,
            ))
        
        # Otherwise use standard GET endpoint
        return cast(Dict[str, Any], self.http.get("/concepts", params=params))
    
    def get_concept_details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.
        
        Args:
            concept_id: The concept ID to get details for
            
        Returns:
            ConceptDetails object
        """
        data = self.http.get(f"/concepts/{concept_id}")
        return ConceptDetails.model_validate(data)
    
    def get_concept_relationships(
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
            
        data = self.http.get(f"/concepts/{concept_id}/relationships", params=params)
        return ConceptRelationship.model_validate(data)
    
    def get_concept_graph(
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
        data = self.http.get(f"/concepts/{concept_id}/relations", params=params)
        return ConceptRelationsGraph.model_validate(data)
