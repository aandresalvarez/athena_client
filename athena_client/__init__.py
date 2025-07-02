"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from .client import AthenaClient
from .concept_explorer import ConceptExplorer, create_concept_explorer
from .db.base import DatabaseConnector
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship

Athena = AthenaClient


def get_sqlalchemy_connector() -> type:
    """Get SQLAlchemyConnector if available.

    Returns:
        SQLAlchemyConnector class if sqlalchemy is available

    Raises:
        ImportError: If sqlalchemy is not available
    """
    try:
        from .db.sqlalchemy_connector import SQLAlchemyConnector

        return SQLAlchemyConnector
    except ImportError as err:
        raise ImportError(
            "sqlalchemy is required for SQLAlchemyConnector. "
            "Install with: pip install 'athena-client[db]'"
        ) from err


__version__ = "1.0.23"

__all__ = [
    "Athena",
    "AthenaClient",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
    "ConceptExplorer",
    "create_concept_explorer",
    "DatabaseConnector",
    "get_sqlalchemy_connector",
]
