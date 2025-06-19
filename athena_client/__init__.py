"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from .client import AthenaClient
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship

Athena = AthenaClient

__version__ = "1.0.4"

__all__ = [
    "Athena",
    "AthenaClient",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
]
