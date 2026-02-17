from unittest.mock import Mock, patch

import pytest

from athena_client.db.sqlalchemy_connector import SQLAlchemyConnector


class TestSQLAlchemyConnector:
    def test_validate_concepts_empty(self):
        engine = Mock()
        connector = SQLAlchemyConnector(engine)

        assert connector.validate_concepts([]) == []
        engine.connect.assert_not_called()

    def test_validate_concepts_all_match(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(1,), (2,)]

        connector = SQLAlchemyConnector(engine)
        result = connector.validate_concepts([1, 2])

        assert result == [1, 2]
        connection.execute.assert_called_once()

    def test_validate_concepts_with_schema(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(1,)]

        connector = SQLAlchemyConnector(engine, schema="cdm")
        connector.validate_concepts([1])

        stmt = connection.execute.call_args[0][0]
        assert "FROM cdm.concept" in stmt.text

    def test_validate_concepts_partial_match(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(2,)]

        connector = SQLAlchemyConnector(engine)
        result = connector.validate_concepts([1, 2])

        assert result == [2]

    def test_validate_concepts_none_match(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = []

        connector = SQLAlchemyConnector(engine)
        result = connector.validate_concepts([1, 2])

        assert result == []

    def test_from_connection_string(self):
        with patch(
            "athena_client.db.sqlalchemy_connector.create_engine"
        ) as mock_create:
            engine = Mock()
            mock_create.return_value = engine
            connector = SQLAlchemyConnector.from_connection_string("sqlite:///:memory:")
            assert connector._engine is engine
            mock_create.assert_called_once_with("sqlite:///:memory:")

    def test_from_connection_string_with_schema(self):
        with patch(
            "athena_client.db.sqlalchemy_connector.create_engine"
        ) as mock_create:
            engine = Mock()
            mock_create.return_value = engine
            connector = SQLAlchemyConnector.from_connection_string(
                "sqlite:///:memory:", schema="cdm"
            )
            assert connector._engine is engine
            assert connector._schema == "cdm"
            mock_create.assert_called_once_with("sqlite:///:memory:")

    def test_invalid_schema(self):
        engine = Mock()
        with pytest.raises(ValueError):
            SQLAlchemyConnector(engine, schema="bad-schema")

    def test_get_descendants_success(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(1,), (2,), (3,)]

        connector = SQLAlchemyConnector(engine)
        result = connector.get_descendants([1])

        assert set(result) == {2, 3}

    def test_get_descendants_with_schema(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(2,)]

        connector = SQLAlchemyConnector(engine, schema="cdm")
        connector.get_descendants([1])

        stmt = connection.execute.call_args[0][0]
        assert "FROM cdm.concept_ancestor" in stmt.text

    def test_get_descendants_no_descendants(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(1,)]

        connector = SQLAlchemyConnector(engine)
        result = connector.get_descendants([1])

        assert result == []

    def test_get_descendants_empty_input(self):
        engine = Mock()
        connector = SQLAlchemyConnector(engine)

        assert connector.get_descendants([]) == []
        engine.connect.assert_not_called()

    def test_get_descendants_invalid_id(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = []

        connector = SQLAlchemyConnector(engine)
        result = connector.get_descendants([999])

        assert result == []

    def test_get_standard_mapping_success(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(10, 100, "S")]

        connector = SQLAlchemyConnector(engine)
        result = connector.get_standard_mapping([10])

        assert result == {10: [100]}

    def test_get_standard_mapping_with_schema(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(10, 100, "S")]

        connector = SQLAlchemyConnector(engine, schema="cdm")
        connector.get_standard_mapping([10])

        stmt = connection.execute.call_args[0][0]
        assert "FROM cdm.concept_relationship" in stmt.text
        assert "JOIN cdm.concept" in stmt.text

    def test_get_standard_mapping_multiple(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(10, 100, "S"), (11, 101, "S")]

        connector = SQLAlchemyConnector(engine)
        result = connector.get_standard_mapping([10, 11, 12])

        assert result == {10: [100], 11: [101]}

    def test_get_standard_mapping_no_mapping(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = []

        connector = SQLAlchemyConnector(engine)
        result = connector.get_standard_mapping([10])

        assert result == {}

    def test_get_standard_mapping_maps_to_non_standard(self):
        engine = Mock()
        connection = Mock()
        engine.connect.return_value.__enter__ = Mock(return_value=connection)
        engine.connect.return_value.__exit__ = Mock(return_value=None)
        connection.execute.return_value = [(10, 100, "C")]

        connector = SQLAlchemyConnector(engine)
        result = connector.get_standard_mapping([10])

        assert result == {}
