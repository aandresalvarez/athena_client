"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from .client import AthenaClient
from .concept_explorer import ConceptExplorer, create_concept_explorer
from .db.base import DatabaseConnector
from .db.sqlalchemy_connector import SQLAlchemyConnector
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship

Athena = AthenaClient

__version__ = "1.0.14"

__all__ = [
    "Athena",
    "AthenaClient",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
    "ConceptExplorer",
    "create_concept_explorer",
    "SQLAlchemyConnector",
    "DatabaseConnector",
]
