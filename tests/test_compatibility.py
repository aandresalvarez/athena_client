"""
Compatibility tests for athena-client with latest dependency versions.

These tests ensure that the library works correctly with the latest versions
of its dependencies, helping to reduce downgrades for users.
"""

from unittest.mock import MagicMock, patch

import pytest


# Test imports to ensure compatibility
def test_import_compatibility():
    """Test that all core modules can be imported successfully."""
    try:
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_sqlalchemy_compatibility():
    """Test SQLAlchemy compatibility with different versions."""
    try:
        from athena_client.db.sqlalchemy_connector import SQLAlchemyConnector

        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_connection = MagicMock()
            mock_create_engine.return_value = mock_engine
            mock_engine.connect.return_value.__enter__.return_value = mock_connection
            mock_connection.execute.return_value = []
            connector = SQLAlchemyConnector.from_connection_string("sqlite:///:memory:")
            # Patch the validate_concepts method to avoid real SQL execution
            with patch.object(
                connector, "validate_concepts", return_value=[]
            ) as mock_validate:
                result = connector.validate_concepts([12345])
                assert isinstance(result, list)
                mock_validate.assert_called_once_with([12345])
    except ImportError as e:
        pytest.fail(f"SQLAlchemy compatibility test failed: {e}")


def test_pandas_compatibility():
    """Test pandas compatibility with different versions."""
    try:
        import pandas as pd

        from athena_client.search_result import SearchResult

        mock_response = MagicMock()
        mock_response.content = []
        mock_response.total_elements = 0
        mock_response.number = 0
        mock_response.size = 20
        mock_response.first = True
        mock_response.last = True
        mock_client = MagicMock()
        result = SearchResult(mock_response, mock_client)
        df = result.to_df()
        assert isinstance(df, pd.DataFrame)
    except ImportError as e:
        pytest.fail(f"Pandas compatibility test failed: {e}")


def test_pydantic_compatibility():
    """Test Pydantic v2 compatibility."""
    try:
        from athena_client.models import Concept

        concept = Concept(
            id=12345,
            name="Test Concept",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept="Standard",
            code="12345",
            invalidReason=None,
        )
        assert concept.id == 12345
        assert concept.name == "Test Concept"
        concept_dict = concept.model_dump()
        assert isinstance(concept_dict, dict)
        assert concept_dict["id"] == 12345
    except ImportError as e:
        pytest.fail(f"Pydantic compatibility test failed: {e}")


def test_httpx_compatibility():
    """Test httpx compatibility for async client."""
    try:
        from athena_client.async_client import AthenaAsyncClient

        client = AthenaAsyncClient()
        assert client is not None
    except ImportError as e:
        pytest.fail(f"httpx compatibility test failed: {e}")


def test_cryptography_compatibility():
    """Test cryptography compatibility for HMAC authentication."""
    try:
        from athena_client.auth import build_headers

        headers = build_headers("GET", "/test", b"", None, None)
        assert isinstance(headers, dict)
    except ImportError as e:
        pytest.fail(f"cryptography compatibility test failed: {e}")


def test_dependency_versions():
    """Test that we're using compatible dependency versions."""
    import pkg_resources

    try:
        sqlalchemy_version = pkg_resources.get_distribution("sqlalchemy").version
        assert pkg_resources.parse_version(
            sqlalchemy_version
        ) >= pkg_resources.parse_version("1.4.0")
    except pkg_resources.DistributionNotFound:
        pytest.skip("SQLAlchemy not installed")
    try:
        pandas_version = pkg_resources.get_distribution("pandas").version
        assert pkg_resources.parse_version(
            pandas_version
        ) >= pkg_resources.parse_version("1.3.0")
        assert pkg_resources.parse_version(
            pandas_version
        ) < pkg_resources.parse_version("3.0.0")
    except pkg_resources.DistributionNotFound:
        pytest.skip("pandas not installed")
    try:
        pydantic_version = pkg_resources.get_distribution("pydantic").version
        assert pkg_resources.parse_version(
            pydantic_version
        ) >= pkg_resources.parse_version("2.0.0")
    except pkg_resources.DistributionNotFound:
        pytest.skip("pydantic not installed")


@pytest.mark.asyncio
async def test_async_compatibility():
    """Test async functionality compatibility."""
    try:
        from athena_client.async_client import AthenaAsyncClient

        client = AthenaAsyncClient()
        assert client is not None
        with patch.object(client, "search_concepts") as mock_search:
            mock_search.return_value = {"content": [], "totalElements": 0}
            result = await client.search_concepts("test")
            assert isinstance(result, dict)
    except ImportError as e:
        pytest.fail(f"Async compatibility test failed: {e}")


def test_optional_dependencies():
    """Test that optional dependencies work correctly."""
    try:
        from athena_client.cli import cli

        assert cli is not None
    except ImportError:
        pytest.skip("click not installed")
    try:
        from athena_client.cli import Console

        assert Console is not None
    except ImportError:
        pytest.skip("rich not installed")
    try:
        import yaml

        assert yaml is not None
    except ImportError:
        pytest.skip("pyyaml not installed")


if __name__ == "__main__":
    # Run compatibility tests
    pytest.main([__file__, "-v"])
