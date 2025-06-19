"""
Pydantic models for Athena API responses.

This module defines Pydantic models for the various responses from the Athena API.
"""

from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Union, cast

import orjson
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, model_validator


def _json_dumps(value: Any, *, default: Any) -> str:
    """Serialize to JSON using orjson."""
    return orjson.dumps(value, default=default).decode()


class BaseModel(PydanticBaseModel):
    """Project-wide Pydantic base model using orjson."""

    model_config: ClassVar[ConfigDict] = cast(
        ConfigDict,
        {
            "populate_by_name": True,
            "extra": "ignore",
        },
    )

    def model_dump_json(self, **kwargs: Any) -> str:
        """Serialize model to JSON using orjson."""
        return orjson.dumps(self.model_dump(**kwargs)).decode()

    @classmethod
    def model_validate_json(
        cls: type["BaseModel"], json_data: Union[str, bytes], **kwargs: Any
    ) -> "BaseModel":
        """Deserialize model from JSON using orjson."""
        return cls.model_validate(orjson.loads(json_data), **kwargs)


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

    STANDARD = "Standard"
    CLASSIFICATION = "Classification"
    NON_STANDARD = "Non-standard"


class Concept(BaseModel):
    """Basic concept information returned in search results."""

    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain: str = Field(..., description="Domain name")
    vocabulary: str = Field(..., description="Vocabulary name")
    className: str = Field(..., description="Concept class name")
    standardConcept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    code: str = Field(..., description="Concept code")
    invalidReason: Optional[str] = Field(None, description="Invalid reason")
    score: Optional[float] = Field(None, description="Search score")


class ConceptSearchResponse(BaseModel):
    """Response from the /concepts search endpoint."""

    content: List[Concept] = Field(..., description="List of concept results")
    pageable: Dict[str, Any] = Field(..., description="Pagination information")
    totalElements: Optional[int] = Field(None, description="Total number of results")
    last: Optional[bool] = Field(None, description="Whether this is the last page")
    totalPages: Optional[int] = Field(None, description="Total number of pages")
    sort: Optional[Dict[str, Any]] = Field(None, description="Sort information")
    first: Optional[bool] = Field(None, description="Whether this is the first page")
    size: Optional[int] = Field(None, description="Page size")
    number: Optional[int] = Field(None, description="Page number")
    numberOfElements: Optional[int] = Field(
        None, description="Number of elements in this page"
    )
    empty: Optional[bool] = Field(None, description="Whether the result is empty")
    facets: Optional[Dict[str, Any]] = Field(None, description="Search facets")


class ConceptDetails(BaseModel):
    """Detailed concept information from the /concepts/{id} endpoint."""

    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domainId: str = Field(..., description="Domain ID")
    vocabularyId: str = Field(..., description="Vocabulary ID")
    conceptClassId: str = Field(..., description="Concept class ID")
    standardConcept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    conceptCode: str = Field(..., description="Concept code")
    invalidReason: Optional[str] = Field(None, description="Invalid reason")
    validStart: str = Field(..., description="Valid start date")
    validEnd: str = Field(..., description="Valid end date")
    synonyms: Optional[List[Union[str, Dict[str, Any]]]] = Field(
        None, description="Concept synonyms"
    )
    validTerm: Optional[Union[str, Dict[str, Any]]] = Field(
        None, description="Valid term"
    )
    vocabularyName: Optional[str] = Field(None, description="Vocabulary name")
    vocabularyVersion: Optional[str] = Field(None, description="Vocabulary version")
    vocabularyReference: Optional[str] = Field(None, description="Vocabulary reference")
    links: Optional[Dict[str, Any]] = Field(
        None, description="HATEOAS links", alias="_links"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_synonyms(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        synonyms = values.get("synonyms")
        if synonyms and isinstance(synonyms, list):
            normalized = []
            for item in synonyms:
                if isinstance(item, str):
                    normalized.append(item)
                elif isinstance(item, dict):
                    # Use 'synonymName' if present, else join all string values
                    if "synonymName" in item:
                        normalized.append(item["synonymName"])
                    else:
                        # Fallback: join all string values in the dict
                        str_values = [
                            str(v) for v in item.values() if isinstance(v, str)
                        ]
                        normalized.append(", ".join(str_values))
            values["synonyms"] = normalized
        return values

    @model_validator(mode="before")
    @classmethod
    def normalize_valid_term(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        valid_term = values.get("validTerm")
        if valid_term and isinstance(valid_term, dict):
            # Extract name from validTerm dict if it's a dictionary
            if "name" in valid_term:
                values["validTerm"] = valid_term["name"]
            else:
                # Fallback: convert to string representation
                values["validTerm"] = str(valid_term)
        return values


class RelationshipItem(BaseModel):
    """Information about a relationship between concepts."""

    targetConceptId: int = Field(..., description="Target concept ID")
    targetConceptName: str = Field(..., description="Target concept name")
    targetVocabularyId: str = Field(..., description="Target vocabulary ID")
    relationshipId: str = Field(..., description="Relationship ID")
    relationshipName: str = Field(..., description="Relationship name")


class RelationshipGroup(BaseModel):
    """Group of relationships with the same type."""

    relationshipName: str = Field(..., description="Relationship name")
    relationships: List[RelationshipItem] = Field(
        ..., description="List of relationships"
    )


class ConceptRelationship(BaseModel):
    """Response from the /concepts/{id}/relationships endpoint."""

    count: int = Field(..., description="Total count of relationships")
    items: List[RelationshipGroup] = Field(
        ..., description="List of relationship groups"
    )


class GraphTerm(BaseModel):
    """Term in the concept relationship graph."""

    id: int = Field(..., description="Term ID")
    name: str = Field(..., description="Term name")
    weight: int = Field(..., description="Term weight")
    depth: int = Field(..., description="Term depth")
    count: int = Field(..., description="Term count")
    isCurrent: bool = Field(..., description="Whether this is the current concept")


class GraphLink(BaseModel):
    """Link in the concept relationship graph."""

    source: int = Field(..., description="Source term ID")
    target: int = Field(..., description="Target term ID")
    relationshipId: Optional[str] = Field(None, description="Relationship ID")
    relationshipName: Optional[str] = Field(None, description="Relationship name")


class ConceptRelationsGraph(BaseModel):
    """Response from the /concepts/{id}/relations endpoint."""

    terms: List[GraphTerm] = Field(..., description="Graph terms")
    links: List[GraphLink] = Field(..., description="Graph links")
    connectionsCount: Optional[int] = Field(None, description="Total connections count")


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
    "GraphLink",
    "GraphTerm",
    "RelationshipGroup",
    "RelationshipItem",
    "Vocabulary",
]
