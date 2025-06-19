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


class TestSearchResult:
    """Test cases for the SearchResult class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_response = Mock(spec=ConceptSearchResponse)

        # Set up default response attributes with correct Concept structure
        self.mock_response.content = [
            Concept(
                id=1,
                name="Test Concept 1",
                domain="Test Domain",
                vocabulary="Test Vocab",
                className="Test Class",
                code="TEST001",
            ),
            Concept(
                id=2,
                name="Test Concept 2",
                domain="Test Domain",
                vocabulary="Test Vocab",
                className="Test Class",
                code="TEST002",
            ),
        ]
        self.mock_response.totalElements = 2
        self.mock_response.totalPages = 1
        self.mock_response.number = 0
        self.mock_response.size = 20
        self.mock_response.first = True
        self.mock_response.last = True
        self.mock_response.facets = {"domain": {"Test": 2}}
        self.mock_response.pageable = None

        self.search_result = SearchResult(self.mock_response, self.mock_client)

    def test_init(self):
        """Test SearchResult initialization."""
        assert self.search_result._response == self.mock_response
        assert self.search_result._client == self.mock_client

    def test_all(self):
        """Test getting all concepts."""
        result = self.search_result.all()
        assert result == self.mock_response.content
        assert len(result) == 2

    def test_top(self):
        """Test getting top N concepts."""
        result = self.search_result.top(1)
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Test Concept 1"

    def test_top_more_than_available(self):
        """Test getting top N concepts when N > available."""
        result = self.search_result.top(5)
        assert len(result) == 2
        assert result == self.mock_response.content

    def test_to_list(self):
        """Test converting to list of dictionaries."""
        result = self.search_result.to_list()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Test Concept 1"

    def test_to_json(self):
        """Test converting to JSON string."""
        # Mock the model_dump_json method
        self.mock_response.model_dump_json.return_value = '{"content": []}'

        result = self.search_result.to_json()
        assert result == '{"content": []}'
        self.mock_response.model_dump_json.assert_called_once()

    @patch("athena_client.search_result.pd")
    def test_to_df_success(self, mock_pd):
        """Test converting to pandas DataFrame successfully."""
        mock_df = Mock()
        mock_pd.DataFrame.return_value = mock_df

        result = self.search_result.to_df()

        assert result == mock_df
        mock_pd.DataFrame.assert_called_once()

    @patch("athena_client.search_result.pd")
    def test_to_df_import_error(self, mock_pd):
        """Test converting to DataFrame when pandas is not available."""
        mock_pd.DataFrame.side_effect = ImportError("No module named 'pandas'")

        with pytest.raises(ImportError) as exc_info:
            self.search_result.to_df()

        assert "pandas is required for DataFrame output" in str(exc_info.value)

    def test_next_page_when_last_page(self):
        """Test next_page when on last page."""
        self.mock_response.last = True

        result = self.search_result.next_page()
        assert result is None

    def test_next_page_when_not_last_page(self):
        """Test next_page when not on last page."""
        self.mock_response.last = False
        self.mock_response.number = 0
        self.mock_response.size = 20

        # Mock the client search method
        mock_next_result = Mock()
        self.mock_client.search.return_value = mock_next_result

        result = self.search_result.next_page()

        assert result == mock_next_result
        self.mock_client.search.assert_called_once_with(query="", page=1, size=20)

    def test_next_page_with_none_values(self):
        """Test next_page when number or size is None."""
        self.mock_response.last = False
        self.mock_response.number = None
        self.mock_response.size = None

        result = self.search_result.next_page()
        assert result is None

    def test_previous_page_when_first_page(self):
        """Test previous_page when on first page."""
        self.mock_response.first = True

        result = self.search_result.previous_page()
        assert result is None

    def test_previous_page_when_not_first_page(self):
        """Test previous_page when not on first page."""
        self.mock_response.first = False
        self.mock_response.number = 1
        self.mock_response.size = 20

        # Mock the client search method
        mock_prev_result = Mock()
        self.mock_client.search.return_value = mock_prev_result

        result = self.search_result.previous_page()

        assert result == mock_prev_result
        self.mock_client.search.assert_called_once_with(query="", page=0, size=20)

    def test_previous_page_with_none_values(self):
        """Test previous_page when number or size is None."""
        self.mock_response.first = False
        self.mock_response.number = None
        self.mock_response.size = None

        result = self.search_result.previous_page()
        assert result is None

    def test_total_elements_direct_field(self):
        """Test total_elements with direct field."""
        self.mock_response.totalElements = 100

        result = self.search_result.total_elements
        assert result == 100

    def test_total_elements_from_pageable(self):
        """Test total_elements from pageable field."""
        self.mock_response.totalElements = None
        self.mock_response.pageable = {"totalElements": 150}

        result = self.search_result.total_elements
        assert result == 150

    def test_total_elements_fallback(self):
        """Test total_elements fallback to content length."""
        self.mock_response.totalElements = None
        self.mock_response.pageable = None

        result = self.search_result.total_elements
        assert result == 2  # Length of content

    def test_total_pages_direct_field(self):
        """Test total_pages with direct field."""
        self.mock_response.totalPages = 5

        result = self.search_result.total_pages
        assert result == 5

    def test_total_pages_calculated_from_pageable(self):
        """Test total_pages calculated from pageable."""
        self.mock_response.totalPages = None
        self.mock_response.pageable = {"totalElements": 100, "pageSize": 20}

        result = self.search_result.total_pages
        assert result == 5  # (100 + 20 - 1) // 20 = 5

    def test_total_pages_fallback(self):
        """Test total_pages fallback."""
        self.mock_response.totalPages = None
        self.mock_response.pageable = None

        result = self.search_result.total_pages
        assert result == 1

    def test_current_page_direct_field(self):
        """Test current_page with direct field."""
        self.mock_response.number = 3

        result = self.search_result.current_page
        assert result == 3

    def test_current_page_from_pageable(self):
        """Test current_page from pageable field."""
        self.mock_response.number = None
        self.mock_response.pageable = {"pageNumber": 2}

        result = self.search_result.current_page
        assert result == 2

    def test_current_page_fallback(self):
        """Test current_page fallback."""
        self.mock_response.number = None
        self.mock_response.pageable = None

        result = self.search_result.current_page
        assert result == 0

    def test_page_size_direct_field(self):
        """Test page_size with direct field."""
        self.mock_response.size = 50

        result = self.search_result.page_size
        assert result == 50

    def test_page_size_from_pageable(self):
        """Test page_size from pageable field."""
        self.mock_response.size = None
        self.mock_response.pageable = {"pageSize": 25}

        result = self.search_result.page_size
        assert result == 25

    def test_page_size_fallback(self):
        """Test page_size fallback to content length."""
        self.mock_response.size = None
        self.mock_response.pageable = None

        result = self.search_result.page_size
        assert result == 2  # Length of content

    def test_facets(self):
        """Test getting facets."""
        result = self.search_result.facets
        assert result == {"domain": {"Test": 2}}

    def test_facets_none(self):
        """Test getting facets when None."""
        self.mock_response.facets = None

        result = self.search_result.facets
        assert result is None

    def test_len(self):
        """Test length of search result."""
        result = len(self.search_result)
        assert result == 2

    def test_getitem(self):
        """Test getting item by index."""
        result = self.search_result[0]
        assert result.id == 1
        assert result.name == "Test Concept 1"

    def test_getitem_negative_index(self):
        """Test getting item with negative index."""
        result = self.search_result[-1]
        assert result.id == 2
        assert result.name == "Test Concept 2"

    def test_iter(self):
        """Test iteration over search result."""
        concepts = list(self.search_result)
        assert len(concepts) == 2
        assert concepts[0].id == 1
        assert concepts[1].id == 2

    def test_empty_search_result(self):
        """Test search result with empty content."""
        self.mock_response.content = []
        self.mock_response.totalElements = 0
        self.mock_response.totalPages = 0
        self.mock_response.number = 0
        self.mock_response.size = 20
        self.mock_response.first = True
        self.mock_response.last = True

        empty_result = SearchResult(self.mock_response, self.mock_client)

        assert len(empty_result) == 0
        assert empty_result.all() == []
        assert empty_result.top(5) == []
        assert empty_result.total_elements == 0
        assert empty_result.total_pages == 0
        assert empty_result.current_page == 0
        assert (
            empty_result.page_size == 20
        )  # Should use the size field, not content length

    def test_search_result_with_pageable_only(self):
        """Test search result with only pageable information."""
        self.mock_response.totalElements = None
        self.mock_response.totalPages = None
        self.mock_response.number = None
        self.mock_response.size = None
        self.mock_response.pageable = {
            "totalElements": 200,
            "totalPages": 10,
            "pageNumber": 3,
            "pageSize": 20,
        }

        result = SearchResult(self.mock_response, self.mock_client)

        assert result.total_elements == 200
        assert result.total_pages == 10
        assert result.current_page == 3
        assert result.page_size == 20

    def test_search_result_edge_cases(self):
        """Test search result with edge case values."""
        # Test with None pageable
        self.mock_response.pageable = None

        result = SearchResult(self.mock_response, self.mock_client)

        # Should use the size field, not content length
        assert result.page_size == 20

        # Test with empty pageable
        self.mock_response.pageable = {}

        result = SearchResult(self.mock_response, self.mock_client)

        # Should use the size field, not content length
        assert result.page_size == 20

    def test_search_result_with_missing_pageable_fields(self):
        """Test search result with missing pageable fields."""
        self.mock_response.totalElements = None
        self.mock_response.totalPages = None
        self.mock_response.number = None
        self.mock_response.size = None
        self.mock_response.pageable = {
            "totalElements": 100,
            # Missing pageSize
        }

        result = SearchResult(self.mock_response, self.mock_client)

        # Should fall back to content length for page_size
        assert result.page_size == 2
        # Should calculate total_pages as 1 (fallback)
        assert result.total_pages == 1

    def test_search_result_with_partial_pageable(self):
        """Test search result with partial pageable information."""
        self.mock_response.totalElements = None
        self.mock_response.totalPages = None
        self.mock_response.number = None
        self.mock_response.size = None
        self.mock_response.pageable = {
            "pageSize": 25,
            # Missing totalElements
        }

        result = SearchResult(self.mock_response, self.mock_client)

        # Should use pageable pageSize
        assert result.page_size == 25
        # Should fall back to content length for total_elements
        assert result.total_elements == 2
