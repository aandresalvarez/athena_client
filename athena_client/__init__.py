"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from .client import AthenaClient
from .concept_explorer import ConceptExplorer, create_concept_explorer
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship

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
