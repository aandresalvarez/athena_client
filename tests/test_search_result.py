"""
Tests for the SearchResult class.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from athena_client.exceptions import ValidationError
from athena_client.search_result import SearchResult


@pytest.fixture
def mock_search_response():
    """Sample search response fixture."""
    return {
        "content": [
            {
                "id": 1127433,
                "name": "Aspirin",
                "domain_id": "Drug",
                "vocabulary_id": "RxNorm",
                "concept_class_id": "Ingredient",
                "standard_concept": "S",
                "concept_code": "1191",
                "valid_start_date": "2000-01-01",
                "valid_end_date": "2099-12-31",
                "invalid_reason": None,
                "domain": {"id": 13, "name": "Drug"},
                "vocabulary": {"id": "RxNorm", "name": "RxNorm"},
                "concept_class": {"id": "Ingredient", "name": "Ingredient"}
            }
        ],
        "pageable": {
            "sort": {"sorted": True, "unsorted": False, "empty": False},
            "pageSize": 20,
            "pageNumber": 0,
            "offset": 0,
            "paged": True,
            "unpaged": False
        },
        "totalElements": 1,
        "last": True,
        "totalPages": 1,
        "first": True,
        "sort": {"sorted": True, "unsorted": False, "empty": False},
        "size": 20,
        "number": 0,
        "numberOfElements": 1,
        "empty": False
    }


def test_search_result_init(mock_search_response):
    """Test SearchResult initialization."""
    result = SearchResult(mock_search_response)
    assert len(result.all()) == 1
    assert result.all()[0].name == "Aspirin"
    assert result.all()[0].id == 1127433


def test_search_result_validation_error():
    """Test validation error on bad data."""
    with pytest.raises(ValidationError):
        SearchResult({"invalid": "data"})


def test_search_result_top(mock_search_response):
    """Test top N results."""
    result = SearchResult(mock_search_response)
    assert len(result.top(1)) == 1
    assert result.top(1)[0].name == "Aspirin"


def test_search_result_to_list(mock_search_response):
    """Test conversion to list of dictionaries."""
    result = SearchResult(mock_search_response)
    data_list = result.to_list()
    assert isinstance(data_list, list)
    assert data_list[0]["name"] == "Aspirin"


def test_search_result_to_json(mock_search_response):
    """Test conversion to JSON."""
    result = SearchResult(mock_search_response)
    json_str = result.to_json()
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed[0]["name"] == "Aspirin"


def test_search_result_to_df(mock_search_response):
    """Test conversion to DataFrame."""
    with patch("pandas.DataFrame") as mock_df:
        mock_df.return_value = MagicMock()
        result = SearchResult(mock_search_response)
        with patch.dict("sys.modules", {"pandas": MagicMock()}):
            df = result.to_df()
            mock_df.assert_called_once()


def test_search_result_to_df_missing_pandas(mock_search_response):
    """Test error when pandas is missing."""
    result = SearchResult(mock_search_response)
    with patch("athena_client.search_result.pd", None):
        with pytest.raises(ImportError):
            result.to_df()


def test_search_result_to_yaml(mock_search_response):
    """Test conversion to YAML."""
    with patch("yaml.dump") as mock_dump:
        mock_dump.return_value = "yaml content"
        result = SearchResult(mock_search_response)
        with patch.dict("sys.modules", {"yaml": MagicMock()}):
            yaml_str = result.to_yaml()
            mock_dump.assert_called_once()
            assert yaml_str == "yaml content"


def test_search_result_to_yaml_missing_pyyaml(mock_search_response):
    """Test error when pyyaml is missing."""
    result = SearchResult(mock_search_response)
    with patch("athena_client.search_result.yaml", None):
        with patch.dict("sys.modules", {"yaml": None}):
            with pytest.raises(ImportError):
                result.to_yaml()


def test_search_result_to_csv(mock_search_response):
    """Test writing to CSV."""
    with patch("athena_client.search_result.SearchResult.to_df") as mock_to_df:
        mock_df = MagicMock()
        mock_to_df.return_value = mock_df
        
        result = SearchResult(mock_search_response)
        result.to_csv("test.csv")
        
        mock_df.to_csv.assert_called_once_with("test.csv", index=False)
