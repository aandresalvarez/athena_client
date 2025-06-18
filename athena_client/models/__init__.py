"""
Pydantic models for Athena API responses.

This module defines Pydantic models for the various responses from the Athena API.
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Domain(BaseModel):
    """Domain information for a concept."""
    
    id: int = Field(..., description="Domain ID")
    name: str = Field(..., description="Domain name")


class Vocabulary(BaseModel):
    """Vocabulary information for a concept."""
    
    id: str = Field(..., description="Vocabulary ID")
    name: str = Field(..., description="Vocabulary name")


class ConceptClass(BaseModel):
    """Concept class information."""
    
    id: str = Field(..., description="Concept class ID")
    name: str = Field(..., description="Concept class name")


class ConceptType(str, Enum):
    """Concept standard type."""
    
    STANDARD = "S"
    CLASSIFICATION = "C"
    NON_STANDARD = ""


class Concept(BaseModel):
    """Basic concept information returned in search results."""
    
    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain_id: str = Field(..., description="Domain ID")
    vocabulary_id: str = Field(..., description="Vocabulary ID")
    concept_class_id: str = Field(..., description="Concept class ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    concept_code: str = Field(..., description="Concept code")
    invalid_reason: Optional[str] = Field(None, description="Invalid reason")
    domain: Domain = Field(..., description="Domain object")
    vocabulary: Vocabulary = Field(..., description="Vocabulary object")
    concept_class: ConceptClass = Field(..., description="Concept class object")
    valid_start_date: str = Field(..., description="Valid start date")
    valid_end_date: str = Field(..., description="Valid end date")


class ConceptSearchResponse(BaseModel):
    """Response from the /concepts search endpoint."""
    
    content: List[Concept] = Field(..., description="List of concept results")
    pageable: Dict[str, Any] = Field(..., description="Pagination information")
    total_elements: int = Field(
        ..., description="Total number of results", alias="totalElements"
    )
    last: bool = Field(..., description="Whether this is the last page")
    total_pages: int = Field(
        ..., description="Total number of pages", alias="totalPages"
    )
    sort: Dict[str, Any] = Field(..., description="Sort information")
    first: bool = Field(..., description="Whether this is the first page")
    size: int = Field(..., description="Page size")
    number: int = Field(..., description="Page number")
    number_of_elements: int = Field(
        ..., description="Number of elements in this page", alias="numberOfElements"
    )
    empty: bool = Field(..., description="Whether the result is empty")


class ConceptDetails(BaseModel):
    """Detailed concept information from the /concepts/{id} endpoint."""
    
    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain_id: str = Field(..., description="Domain ID")
    vocabulary_id: str = Field(..., description="Vocabulary ID")
    concept_class_id: str = Field(..., description="Concept class ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    concept_code: str = Field(..., description="Concept code")
    invalid_reason: Optional[str] = Field(None, description="Invalid reason")
    domain: Domain = Field(..., description="Domain object")
    vocabulary: Vocabulary = Field(..., description="Vocabulary object")
    concept_class: ConceptClass = Field(..., description="Concept class object")
    valid_start_date: str = Field(..., description="Valid start date")
    valid_end_date: str = Field(..., description="Valid end date")
    # Additional fields specific to details
    synonyms: Optional[List[str]] = Field(None, description="Concept synonyms")
    additional_information: Optional[Dict[str, Any]] = Field(
        None, description="Additional information"
    )


class RelationshipItem(BaseModel):
    """Information about a relationship between concepts."""
    
    relationship_id: str = Field(..., description="Relationship ID")
    relationship_name: str = Field(..., description="Relationship name")
    relationship_concept_id: int = Field(..., description="Relationship concept ID")


class ConceptRelationship(BaseModel):
    """Response from the /concepts/{id}/relationships endpoint."""
    
    concept_id: int = Field(..., description="Concept ID")
    relationships: List[RelationshipItem] = Field(
        ..., description="List of relationships"
    )


class GraphNode(BaseModel):
    """Node in the concept relationship graph."""
    
    id: int = Field(..., description="Node ID")
    name: str = Field(..., description="Node name")
    concept_id: int = Field(..., description="Concept ID")
    domain_id: str = Field(..., description="Domain ID")
    standard_concept: Optional[ConceptType] = Field(None, description="Standard concept flag")


class GraphEdge(BaseModel):
    """Edge in the concept relationship graph."""
    
    source: int = Field(..., description="Source node ID")
    target: int = Field(..., description="Target node ID")
    relationship_id: str = Field(..., description="Relationship ID")


class ConceptRelationsGraph(BaseModel):
    """Response from the /concepts/{id}/relations endpoint."""
    
    nodes: List[GraphNode] = Field(..., description="Graph nodes")
    edges: List[GraphEdge] = Field(..., description="Graph edges")


# Re-export models
__all__ = [
    "Concept",
    "ConceptClass",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
    "ConceptSearchResponse",
    "ConceptType",
    "Domain",
    "GraphEdge",
    "GraphNode",
    "RelationshipItem",
    "Vocabulary",
]
