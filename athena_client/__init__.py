"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from .client import AthenaClient
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship
from .concept_explorer import ConceptExplorer, create_concept_explorer

Athena = AthenaClient

__version__ = "1.0.5"

__all__ = [
    "Athena",
    "AthenaClient",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
    "ConceptExplorer",
    "create_concept_explorer",
]
