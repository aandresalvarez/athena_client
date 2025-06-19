from typing import List

from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine


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

    @staticmethod
    def from_connection_string(connection_string: str) -> "SQLAlchemyConnector":
        engine = create_engine(connection_string)
        return SQLAlchemyConnector(engine)
