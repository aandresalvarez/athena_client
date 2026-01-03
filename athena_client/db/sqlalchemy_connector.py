from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

try:
    # Only import these if needed, do not import sqlalchemy at the top level
    from sqlalchemy import bindparam, create_engine, text

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class SQLAlchemyConnector:
    """Database connector using SQLAlchemy Core."""

    def __init__(self, engine: "Engine") -> None:
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "sqlalchemy is required for database features. Install with: "
                "pip install athena-client[db] or pip install sqlalchemy"
            )
        self._engine = engine

    def validate_concepts(self, concept_ids: List[int]) -> List[int]:
        if not concept_ids:
            return []

        # Chunk the IDs to avoid database parameter limits
        chunk_size = 1000
        validated_ids = []
        
        with self._engine.connect() as connection:
            for i in range(0, len(concept_ids), chunk_size):
                chunk = list(concept_ids)[i : i + chunk_size]
                stmt = text(
                    """
                        SELECT concept_id
                        FROM concept
                        WHERE concept_id IN :ids AND standard_concept = 'S'
                        """
                ).bindparams(bindparam("ids", expanding=True))
                
                result = connection.execute(stmt, {"ids": chunk})
                validated_ids.extend([row[0] for row in result])

        return validated_ids

    def get_descendants(self, concept_ids: List[int]) -> List[int]:
        """Retrieve descendant concept IDs for the given ancestors."""
        if not concept_ids:
            return []

        # Chunk the IDs to avoid database parameter limits
        chunk_size = 1000
        descendant_ids = []
        
        with self._engine.connect() as connection:
            for i in range(0, len(concept_ids), chunk_size):
                chunk = list(concept_ids)[i : i + chunk_size]
                stmt = text(
                    """
                        SELECT descendant_concept_id
                        FROM concept_ancestor
                        WHERE ancestor_concept_id IN :ids
                        """
                ).bindparams(bindparam("ids", expanding=True))
                
                result = connection.execute(stmt, {"ids": chunk})
                descendant_ids.extend([row[0] for row in result])

        return list(set(descendant_ids) - set(concept_ids))

    def get_standard_mapping(
        self, non_standard_concept_ids: List[int]
    ) -> Dict[int, List[int]]:
        """Find standard mappings for the given non-standard concept IDs."""
        if not non_standard_concept_ids:
            return {}

        # Chunk the IDs to avoid database parameter limits
        chunk_size = 1000
        mapping: Dict[int, List[int]] = {}
        
        with self._engine.connect() as connection:
            for i in range(0, len(non_standard_concept_ids), chunk_size):
                chunk = list(non_standard_concept_ids)[i : i + chunk_size]
                stmt = text(
                    """
                    SELECT cr.concept_id_1, cr.concept_id_2, c2.standard_concept
                    FROM concept_relationship cr
                    JOIN concept c2 ON cr.concept_id_2 = c2.concept_id
                    WHERE cr.concept_id_1 IN :ids
                      AND cr.relationship_id = 'Maps to'
                      AND cr.invalid_reason IS NULL
                    """
                ).bindparams(bindparam("ids", expanding=True))
                
                result = connection.execute(stmt, {"ids": chunk})
                for row in result:
                    concept_id_1, concept_id_2, standard_flag = row
                    if standard_flag == "S":
                        if concept_id_1 not in mapping:
                            mapping[concept_id_1] = []
                        mapping[concept_id_1].append(concept_id_2)

        return mapping

    @staticmethod
    def from_connection_string(connection_string: str) -> "SQLAlchemyConnector":
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "sqlalchemy is required for database features. Install with: "
                "pip install athena-client[db] or pip install sqlalchemy"
            )
        engine = create_engine(connection_string)
        return SQLAlchemyConnector(engine)
