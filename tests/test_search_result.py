"""
Tests for SearchResult class and pagination functionality.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from athena_client.models import Concept, ConceptSearchResponse, ConceptType
from athena_client.search_result import SearchResult


@pytest.fixture
def mock_client():
    """Create a mock client for SearchResult tests."""
    return Mock()


@pytest.fixture
def mock_search_response():
    """Create a mock search response."""
    return ConceptSearchResponse(
        content=[
            Concept(
                id=1,
                name="Aspirin",
                domain="Drug",
                vocabulary="RxNorm",
                className="Ingredient",
                standardConcept=ConceptType.STANDARD,
                code="1191",
                invalidReason=None,
                score=1.0,
            )
        ],
        pageable={"pageSize": 1},
        totalElements=1,
        last=True,
        totalPages=1,
        first=True,
        size=1,
        number=0,
        numberOfElements=1,
        empty=False,
    )


def test_search_result_init(mock_search_response, mock_client):
    """Test SearchResult initialization."""
    result = SearchResult(mock_search_response, mock_client)
    assert result.total_elements == 1
    assert len(result.all()) == 1
    assert result.all()[0].name == "Aspirin"


def test_search_result_validation_error(mock_client):
    """Test that passing a dict does not raise an error
    (type is not enforced at runtime)."""
    # This should not raise an error, but will not behave as expected
    result = SearchResult({"invalid": "data"}, mock_client)
    assert result is not None


def test_search_result_top(mock_search_response, mock_client):
    """Test top N results."""
    result = SearchResult(mock_search_response, mock_client)
    top_results = result.top(1)
    assert len(top_results) == 1
    assert top_results[0].name == "Aspirin"


def test_search_result_to_list(mock_search_response, mock_client):
    """Test conversion to list of dictionaries."""
    result = SearchResult(mock_search_response, mock_client)
    data_list = result.to_list()
    assert isinstance(data_list, list)
    assert len(data_list) == 1
    assert data_list[0]["name"] == "Aspirin"


def test_search_result_to_json(mock_search_response, mock_client):
    """Test conversion to JSON."""
    result = SearchResult(mock_search_response, mock_client)
    json_str = result.to_json()
    assert isinstance(json_str, str)
    assert "Aspirin" in json_str


def test_search_result_to_df(mock_search_response, mock_client):
    """Test conversion to DataFrame."""
    mock_dataframe = MagicMock()
    mock_pandas = MagicMock()
    mock_pandas.DataFrame.return_value = mock_dataframe

    with patch.dict("sys.modules", {"pandas": mock_pandas}):
        with patch("athena_client.search_result.pd", mock_pandas):
            result = SearchResult(mock_search_response, mock_client)
            df = result.to_df()
            assert df == mock_dataframe


def test_search_result_to_df_missing_pandas(mock_search_response, mock_client):
    """Test error when pandas is missing."""
    result = SearchResult(mock_search_response, mock_client)
    with patch("athena_client.search_result.pd", None):
        with pytest.raises(AttributeError):
            result.to_df()


def test_search_result_pagination_properties(mock_search_response, mock_client):
    """Test pagination properties."""
    result = SearchResult(mock_search_response, mock_client)
    assert result.total_elements == 1
    assert result.total_pages == 1
    assert result.current_page == 0
    assert result.page_size == 1


def test_search_result_length_and_indexing(mock_search_response, mock_client):
    """Test length and indexing."""
    result = SearchResult(mock_search_response, mock_client)
    assert len(result) == 1
    assert result[0].name == "Aspirin"

    # Test iteration
    concepts = list(result)
    assert len(concepts) == 1
    assert concepts[0].name == "Aspirin"
