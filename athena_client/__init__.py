"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from typing import Any, Dict, Optional

from .client import AthenaClient
Athena = AthenaClient

from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship
__version__ = "1.0.4"
