from unittest.mock import Mock, patch

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
