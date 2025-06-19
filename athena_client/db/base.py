from typing import List, Protocol


class DatabaseConnector(Protocol):
    """Protocol for database connectors."""

    def validate_concepts(self, concept_ids: List[int]) -> List[int]:
        """Validate concept IDs against the local database."""
        ...

    def get_descendants(self, concept_ids: List[int]) -> List[int]:
        """Return descendant concept IDs for the given ancestors."""
        ...
