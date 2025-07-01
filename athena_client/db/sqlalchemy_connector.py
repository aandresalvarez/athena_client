try:
    # Only import these if needed, do not import sqlalchemy at the top level
    from sqlalchemy import bindparam, create_engine, text
    from sqlalchemy.engine import Engine
except ImportError as e:
    raise ImportError(
        "sqlalchemy is required for database features. Install with: "
        "pip install athena-client[db] or pip install sqlalchemy"
    ) from e
from typing import Dict, List


class SQLAlchemyConnector:
    """Database connector using SQLAlchemy Core."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def validate_concepts(self, concept_ids: List[int]) -> List[int]:
        if not concept_ids:
            return []

        stmt = text(
            """
                SELECT concept_id
                FROM concept
                WHERE concept_id IN :ids AND standard_concept = 'S'
                """
        ).bindparams(bindparam("ids", expanding=True))

        with self._engine.connect() as connection:
            result = connection.execute(stmt, {"ids": list(concept_ids)})
            validated_ids = [row[0] for row in result]

        return validated_ids

    def get_descendants(self, concept_ids: List[int]) -> List[int]:
        """Retrieve descendant concept IDs for the given ancestors."""
        if not concept_ids:
            return []

        stmt = text(
            """
                SELECT descendant_concept_id
                FROM concept_ancestor
                WHERE ancestor_concept_id IN :ids
                """
        ).bindparams(bindparam("ids", expanding=True))

        with self._engine.connect() as connection:
            result = connection.execute(stmt, {"ids": list(concept_ids)})
            descendant_ids = [row[0] for row in result]

        return list(set(descendant_ids) - set(concept_ids))

    def get_standard_mapping(
        self, non_standard_concept_ids: List[int]
    ) -> Dict[int, int]:
        """Find standard mappings for the given non-standard concept IDs."""
        if not non_standard_concept_ids:
            return {}

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

        with self._engine.connect() as connection:
            result = connection.execute(stmt, {"ids": list(non_standard_concept_ids)})
            mapping: Dict[int, int] = {}
            for row in result:
                concept_id_1, concept_id_2, standard_flag = row
                if standard_flag == "S" and concept_id_1 not in mapping:
                    mapping[concept_id_1] = concept_id_2

        return mapping

    @staticmethod
    def from_connection_string(connection_string: str) -> "SQLAlchemyConnector":
        engine = create_engine(connection_string)
        return SQLAlchemyConnector(engine)
