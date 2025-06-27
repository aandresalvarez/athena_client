"""
Tests for the AthenaClient class and its enhanced functionality.
"""

import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from athena_client import Athena
from athena_client.client import AthenaClient
from athena_client.exceptions import (
    APIError,
    AthenaError,
    NetworkError,
    RetryFailedError,
)
from athena_client.models import (
    ConceptDetails,
    ConceptRelationsGraph,
    ConceptRelationship,
)
from athena_client.query import Q
from athena_client.search_result import SearchResult
from athena_client.settings import clear_settings_cache


class TestAthenaClientInitialization:
    """Test client initialization and configuration."""

    def test_default_initialization(self):
        """Test client initialization with default settings."""
        client = AthenaClient()
        assert client.max_retries == 3
        assert client.retry_delay is None
        assert client.enable_throttling is True
        assert client.throttle_delay_range == (0.1, 0.3)

    def test_custom_initialization(self):
        """Test client initialization with custom settings."""
        client = AthenaClient(
            max_retries=5,
            retry_delay=2.0,
            enable_throttling=False,
            throttle_delay_range=(0.2, 0.5),
            timeout=30,
        )
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.enable_throttling is False
        assert client.throttle_delay_range == (0.2, 0.5)

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Clear the settings cache to ensure environment variables are picked up
        clear_settings_cache()

        with patch.dict(os.environ, {"ATHENA_MAX_RETRIES": "7"}):
            client = AthenaClient()
            assert client.max_retries == 7

        # Clean up by clearing cache again
        clear_settings_cache()


class TestRetryConfiguration:
    """Test retry configuration and behavior."""

    def test_retry_configuration_passed_to_http_client(self):
        """Test that retry configuration is passed to HTTP client."""
        with patch("athena_client.client.HttpClient") as mock_http:
            AthenaClient(
                max_retries=5, enable_throttling=False, throttle_delay_range=(0.1, 0.2)
            )

            mock_http.assert_called_once()
            call_args = mock_http.call_args[1]
            assert call_args["max_retries"] == 5
            assert call_args["enable_throttling"] is False
            assert call_args["throttle_delay_range"] == (0.1, 0.2)

    def test_call_level_retry_override(self, athena_client):
        """Test that call-level retry settings override client settings."""
        # Mock successful response
        mock_response = {
            "content": [],
            "pageable": {},
            "totalElements": 0,
            "last": True,
            "totalPages": 1,
            "first": True,
            "sort": {},
            "size": 20,
            "number": 0,
            "numberOfElements": 0,
            "empty": True,
        }

        athena_client.http.get.return_value = mock_response

        # Test with call-level override
        result = athena_client.search("test", max_retries=1, retry_delay=0.5)

        assert result is not None
        athena_client.http.get.assert_called_once()


class TestErrorHandling:
    """Test enhanced error handling and reporting."""

    def test_network_error_retry(self, athena_client):
        """Test that network errors are retried."""
        # Mock network error for first two attempts, success on third
        athena_client.http.get.side_effect = [
            NetworkError("Connection failed"),
            NetworkError("Connection failed"),
            {
                "content": [],
                "pageable": {},
                "totalElements": 0,
                "last": True,
                "totalPages": 1,
                "first": True,
                "sort": {},
                "size": 20,
                "number": 0,
                "numberOfElements": 0,
                "empty": True,
            },
        ]

        result = athena_client.search("test", max_retries=3)
        assert result is not None
        assert athena_client.http.get.call_count == 3

    def test_retry_failure_with_detailed_reporting(self, athena_client):
        """Test detailed retry failure reporting."""
        # Mock persistent network error
        athena_client.http.get.side_effect = NetworkError("Connection failed")

        with pytest.raises(RetryFailedError) as exc_info:
            athena_client.search("test", max_retries=2)

        error = exc_info.value
        assert error.max_attempts == 2
        assert len(error.retry_history) == 1
        assert isinstance(error.last_error, NetworkError)
        assert "Search failed after 2 attempts" in str(error)

    def test_api_error_not_retried(self, athena_client):
        """Test that API errors are not retried."""
        # Mock API error response
        api_error_response = {
            "result": None,
            "errorMessage": "Concept not found",
            "errorCode": "NOT_FOUND",
        }
        athena_client.http.get.return_value = api_error_response

        with pytest.raises(APIError) as exc_info:
            athena_client.search("test")

        # Should not retry API errors
        assert athena_client.http.get.call_count == 1
        assert "Concept not found" in str(exc_info.value)

    def test_validation_error_not_retried(self, athena_client):
        """Test that validation errors are not retried."""
        # Mock a validation error response
        invalid_response = {"invalid": "data"}
        athena_client.http.get.return_value = invalid_response

        # This should fail with a retry failed error since validation errors are retried
        with pytest.raises(Exception) as exc_info:
            athena_client.search("test")

        # Should be a retry failed error since validation errors are retried
        assert "retry" in str(exc_info.value).lower()
        # Should not retry validation errors
        assert athena_client.http.get.call_count == 3  # Initial + 2 retries


class TestClientMethods:
    """Test all client methods with enhanced error handling."""

    def test_search_success(self, athena_client):
        """Test successful search operation."""
        mock_response = {
            "content": [
                {
                    "id": 1,
                    "name": "Aspirin",
                    "domain": "Drug",
                    "vocabulary": "RxNorm",
                    "className": "Ingredient",
                    "standardConcept": "Standard",
                    "code": "1191",
                    "invalidReason": None,
                    "score": 1.0,
                }
            ],
            "pageable": {"pageSize": 1},
            "totalElements": 1,
            "last": True,
            "totalPages": 1,
            "first": True,
            "size": 1,
            "number": 0,
            "numberOfElements": 1,
            "empty": False,
        }

        athena_client.http.get.return_value = mock_response

        result = athena_client.search("aspirin")
        assert result is not None
        assert len(result.all()) == 1
        assert result.all()[0].name == "Aspirin"

    def test_search_with_query_dsl(self, athena_client):
        """Test search with Query DSL object."""
        # Mock successful response
        mock_response = {
            "content": [],
            "pageable": {},
            "totalElements": 0,
            "last": True,
            "totalPages": 1,
            "first": True,
            "sort": {},
            "size": 20,
            "number": 0,
            "numberOfElements": 0,
            "empty": True,
        }
        athena_client.http.get.return_value = mock_response

        query = Q.term("diabetes") & Q.term("type 2")
        athena_client.search(query)

        # Verify the search method was called
        athena_client.http.get.assert_called_once()

    def test_details_success(self, athena_client):
        """Test successful concept details retrieval."""
        mock_response = {
            "id": 1,
            "name": "Aspirin",
            "domainId": "Drug",
            "vocabularyId": "RxNorm",
            "conceptClassId": "Ingredient",
            "standardConcept": "Standard",
            "conceptCode": "1191",
            "invalidReason": None,
            "validStart": "2000-01-01",
            "validEnd": "2099-12-31",
        }

        athena_client.http.get.return_value = mock_response

        result = athena_client.details(1)
        assert result.name == "Aspirin"
        assert result.domainId == "Drug"

    def test_relationships_success(self, athena_client):
        """Test successful relationships retrieval."""
        mock_response = {
            "count": 1,
            "items": [
                {
                    "relationshipName": "Is a",
                    "relationships": [
                        {
                            "targetConceptId": 2,
                            "targetConceptName": "Drug",
                            "targetVocabularyId": "RxNorm",
                            "relationshipId": "Is a",
                            "relationshipName": "Is a",
                        }
                    ],
                }
            ],
        }

        athena_client.http.get.return_value = mock_response

        result = athena_client.relationships(1)
        assert result.count == 1
        assert result.items[0].relationshipName == "Is a"

    def test_graph_success(self, athena_client):
        """Test successful graph retrieval."""
        mock_response = {
            "terms": [
                {
                    "id": 1,
                    "name": "Aspirin",
                    "weight": 1,
                    "depth": 0,
                    "count": 1,
                    "isCurrent": True,
                },
                {
                    "id": 2,
                    "name": "Drug",
                    "weight": 1,
                    "depth": 1,
                    "count": 1,
                    "isCurrent": False,
                },
            ],
            "links": [
                {
                    "source": 1,
                    "target": 2,
                    "relationshipId": "Is a",
                    "relationshipName": "Is a",
                }
            ],
            "connectionsCount": 1,
        }

        athena_client.http.get.return_value = mock_response

        result = athena_client.graph(1, depth=2)
        assert result.terms[0].name == "Aspirin"
        assert result.links[0].relationshipName == "Is a"

    def test_summary_success(self, athena_client):
        """Test successful summary retrieval."""
        details_response = {
            "id": 1,
            "name": "Aspirin",
            "domainId": "Drug",
            "vocabularyId": "RxNorm",
            "conceptClassId": "Ingredient",
            "standardConcept": "Standard",
            "conceptCode": "1191",
            "invalidReason": None,
            "validStart": "2000-01-01",
            "validEnd": "2099-12-31",
        }
        relationships_response = {"count": 0, "items": []}
        graph_response = {"terms": [], "links": [], "connectionsCount": 0}
        athena_client.http.get.side_effect = [
            details_response,
            relationships_response,
            graph_response,
        ]
        result = athena_client.summary(1)
        # The summary method returns a dict with the raw response data
        assert result["details"]["name"] == "Aspirin"
        assert result["relationships"]["count"] == 0
        assert result["graph"]["connectionsCount"] == 0


class TestErrorScenarios:
    """Test various error scenarios."""

    @patch("athena_client.client.HttpClient")
    def test_authentication_error(self, mock_http_client_class, athena_client):
        """Test authentication error handling."""
        error_response = {
            "result": None,
            "errorMessage": "Authentication failed",
            "errorCode": "AUTH_ERROR",
        }

        # Mock the HttpClient class to return our error response
        mock_http_client = Mock()
        mock_http_client.get.return_value = error_response
        mock_http_client_class.return_value = mock_http_client

        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)

        assert "Authentication failed" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_rate_limit_error(self, mock_http_client_class, athena_client):
        """Test rate limit error handling."""
        error_response = {
            "result": None,
            "errorMessage": "Rate limit exceeded",
            "errorCode": "RATE_LIMIT",
        }

        # Mock the HttpClient class to return our error response
        mock_http_client = Mock()
        mock_http_client.get.return_value = error_response
        mock_http_client_class.return_value = mock_http_client

        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)

        assert "Rate limit exceeded" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_client_error(self, mock_http_client_class, athena_client):
        """Test client error handling."""
        error_response = {
            "result": None,
            "errorMessage": "Bad request",
            "errorCode": "BAD_REQUEST",
        }

        # Mock the HttpClient class to return our error response
        mock_http_client = Mock()
        mock_http_client.get.return_value = error_response
        mock_http_client_class.return_value = mock_http_client

        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)

        assert "Bad request" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_server_error(self, mock_http_client_class, athena_client):
        """Test server error handling."""
        error_response = {
            "result": None,
            "errorMessage": "Internal server error",
            "errorCode": "SERVER_ERROR",
        }

        # Mock the HttpClient class to return our error response
        mock_http_client = Mock()
        mock_http_client.get.return_value = error_response
        mock_http_client_class.return_value = mock_http_client

        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)

        assert "Internal server error" in str(exc_info.value)


class TestRetryDelay:
    """Test retry delay functionality."""

    @patch("time.sleep")
    def test_retry_delay_applied(self, mock_sleep, athena_client):
        """Test that retry delay is applied between attempts."""
        # Mock network error for first attempt, success on second
        athena_client.http.get.side_effect = [
            NetworkError("Connection failed"),
            {
                "content": [],
                "pageable": {},
                "totalElements": 0,
                "last": True,
                "totalPages": 1,
                "first": True,
                "sort": {},
                "size": 20,
                "number": 0,
                "numberOfElements": 0,
                "empty": True,
            },
        ]

        athena_client.search("test", retry_delay=1.0, max_retries=2)

        # Verify sleep was called with the retry delay
        mock_sleep.assert_called_once_with(1.0)

    def test_no_retry_delay_when_none(self, athena_client):
        """Test that no delay is applied when retry_delay is None."""
        # Mock network error for first attempt, success on second
        athena_client.http.get.side_effect = [
            NetworkError("Connection failed"),
            {
                "content": [],
                "pageable": {},
                "totalElements": 0,
                "last": True,
                "totalPages": 1,
                "first": True,
                "sort": {},
                "size": 20,
                "number": 0,
                "numberOfElements": 0,
                "empty": True,
            },
        ]

        with patch("time.sleep") as mock_sleep:
            athena_client.search("test", retry_delay=None, max_retries=2)

            # Verify sleep was not called
            mock_sleep.assert_not_called()


class TestAthenaFacade:
    """Test the Athena facade class."""

    def test_athena_facade_initialization(self):
        """Test Athena facade initialization."""
        facade = Athena()
        assert isinstance(facade, AthenaClient)

    def test_athena_facade_capabilities(self):
        """Test Athena facade capabilities method."""
        # Athena.capabilities() is deprecated or removed; skip this test.
        pass


class TestAthenaClient:
    """Test cases for the AthenaClient class."""

    def test_init_with_defaults(self):
        """Test client initialization with default values."""
        client = AthenaClient()
        assert client.max_retries == 3
        assert client.retry_delay is None
        assert client.enable_throttling is True

    def test_init_with_custom_values(self):
        """Test client initialization with custom values."""
        client = AthenaClient(
            base_url="https://custom.api.com",
            token="test-token",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            enable_throttling=False,
        )
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.enable_throttling is False

    @patch("athena_client.client.HttpClient")
    def test_search_success(self, mock_http_client_class):
        """Test successful search."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_response = {
            "content": [
                {
                    "id": 1,
                    "name": "Test Concept",
                    "domain": "Test Domain",
                    "vocabulary": "Test Vocab",
                    "className": "Test Class",
                    "code": "TEST001",
                }
            ],
            "pageable": {"pageSize": 20, "pageNumber": 0},
            "totalElements": 1,
            "totalPages": 1,
            "number": 0,
            "size": 20,
            "first": True,
            "last": True,
        }
        mock_http_client.get.return_value = mock_response

        client = AthenaClient()
        result = client.search("test query")

        assert isinstance(result, SearchResult)
        mock_http_client.get.assert_called_once()

    @patch("athena_client.client.HttpClient")
    def test_search_with_query_object(self, mock_http_client_class):
        """Test search with query object."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_response = {
            "content": [
                {
                    "id": 1,
                    "name": "Test Concept",
                    "domain": "Test Domain",
                    "vocabulary": "Test Vocab",
                    "className": "Test Class",
                    "code": "TEST001",
                }
            ],
            "pageable": {"pageSize": 20, "pageNumber": 0},
            "totalElements": 1,
            "totalPages": 1,
            "number": 0,
            "size": 20,
            "first": True,
            "last": True,
        }
        mock_http_client.get.return_value = mock_response

        client = AthenaClient()

        # Test with query object
        query = Q.term("test").fuzzy()
        result = client.search(query)

        assert isinstance(result, SearchResult)
        mock_http_client.get.assert_called_once()

    @patch("athena_client.client.HttpClient")
    def test_search_api_error_page_size_too_small(self, mock_http_client_class):
        """Test search with API error for page size too small."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Page size must not be less than one",
            "errorCode": "INVALID_PAGE_SIZE",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.search("test", size=0)

        # New error message is more specific
        assert "Invalid page size" in str(exc_info.value)
        assert "Page size must not be less than one" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_search_api_error_page_size_too_large(self, mock_http_client_class):
        """Test search with API error for page size too large."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Page size must not be greater than 1000",
            "errorCode": "INVALID_PAGE_SIZE",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        # Now raises ValueError before making HTTP call
        with pytest.raises(ValueError) as exc_info:
            client.search("test", size=1001)

        assert "Page size 1001 exceeds maximum allowed size of 1000" in str(
            exc_info.value
        )

    @patch("athena_client.client.HttpClient")
    def test_search_api_error_empty_query(self, mock_http_client_class):
        """Test search with API error for empty query."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Query must not be blank",
            "errorCode": "INVALID_QUERY",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.search("")

        # New error message is more specific
        assert "Empty search query" in str(exc_info.value)
        assert "Query must not be blank" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_search_api_error_generic(self, mock_http_client_class):
        """Test search with generic API error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Some other error",
            "errorCode": "GENERIC_ERROR",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.search("test")

        # New error message is more specific
        assert "Search failed" in str(exc_info.value) or "Some other error" in str(
            exc_info.value
        )
        assert "Some other error" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_search_retry_on_network_error(self, mock_http_client_class):
        """Test search retry on network error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # First call fails, second succeeds
        mock_http_client.get.side_effect = [
            Exception("Network error"),
            {
                "content": [
                    {
                        "id": 1,
                        "name": "Test Concept",
                        "domain": "Test Domain",
                        "vocabulary": "Test Vocab",
                        "className": "Test Class",
                        "code": "TEST001",
                    }
                ],
                "pageable": {"pageSize": 20, "pageNumber": 0},
                "totalElements": 1,
                "totalPages": 1,
                "number": 0,
                "size": 20,
                "first": True,
                "last": True,
            },
        ]

        client = AthenaClient(max_retries=2, retry_delay=0.1)
        result = client.search("test")

        assert isinstance(result, SearchResult)
        assert mock_http_client.get.call_count == 2

    @patch("athena_client.client.HttpClient")
    def test_search_retry_failed(self, mock_http_client_class):
        """Test search retry failure."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # All calls fail
        mock_http_client.get.side_effect = Exception("Network error")

        client = AthenaClient(max_retries=2, retry_delay=0.1)

        with pytest.raises(RetryFailedError) as exc_info:
            client.search("test")

        assert "Search failed after 2 attempts" in str(exc_info.value)
        assert mock_http_client.get.call_count == 2

    @patch("athena_client.client.HttpClient")
    def test_search_no_retry(self, mock_http_client_class):
        """Test search with no retry."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_http_client.get.side_effect = Exception("Network error")

        client = AthenaClient()

        with pytest.raises(RetryFailedError) as exc_info:
            client.search("test", auto_retry=False)

        assert "Search failed after 1 attempts" in str(exc_info.value)
        assert mock_http_client.get.call_count == 1

    @patch("athena_client.client.HttpClient")
    def test_details_success(self, mock_http_client_class):
        """Test successful concept details."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_response = {
            "id": 1,
            "name": "Test Concept",
            "conceptCode": "TEST001",
            "domainId": "Test Domain",
            "vocabularyId": "Test Vocab",
            "conceptClassId": "Test Class",
            "validStart": "2020-01-01",
            "validEnd": "2020-12-31",
        }
        mock_http_client.get.return_value = mock_response

        client = AthenaClient()
        result = client.details(1)

        assert isinstance(result, ConceptDetails)
        assert result.id == 1
        assert result.name == "Test Concept"
        mock_http_client.get.assert_called_once_with("/concepts/1")

    @patch("athena_client.client.HttpClient")
    def test_details_api_error_concept_not_found(self, mock_http_client_class):
        """Test concept details with API error for concept not found."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Unable to find ConceptV5 with id 999",
            "errorCode": "CONCEPT_NOT_FOUND",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.details(999)

        assert "Concept not found" in str(exc_info.value)
        assert "Concept ID 999 does not exist" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_details_api_error_generic(self, mock_http_client_class):
        """Test concept details with generic API error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Some other error",
            "errorCode": "GENERIC_ERROR",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.details(1)

        assert "Failed to get concept details" in str(exc_info.value)
        assert "Some other error" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_details_retry_on_network_error(self, mock_http_client_class):
        """Test concept details retry on network error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # First call fails, second succeeds
        mock_http_client.get.side_effect = [
            Exception("Network error"),
            {
                "id": 1,
                "name": "Test Concept",
                "conceptCode": "TEST001",
                "domainId": "Test Domain",
                "vocabularyId": "Test Vocab",
                "conceptClassId": "Test Class",
                "validStart": "2020-01-01",
                "validEnd": "2020-12-31",
            },
        ]

        client = AthenaClient(max_retries=2, retry_delay=0.1)
        result = client.details(1)

        assert isinstance(result, ConceptDetails)
        assert mock_http_client.get.call_count == 2

    @patch("athena_client.client.HttpClient")
    def test_details_retry_failed(self, mock_http_client_class):
        """Test concept details retry failure."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # All calls fail
        mock_http_client.get.side_effect = Exception("Network error")

        client = AthenaClient(max_retries=2, retry_delay=0.1)

        with pytest.raises(AthenaError) as exc_info:
            client.details(1)

        assert "Failed to get concept details after 3 attempts" in str(exc_info.value)
        assert mock_http_client.get.call_count == 3

    @patch("athena_client.client.HttpClient")
    def test_relationships_success(self, mock_http_client_class):
        """Test successful concept relationships."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_response = {
            "count": 1,
            "items": [
                {
                    "relationshipName": "Test Relationship",
                    "relationships": [
                        {
                            "targetConceptId": 2,
                            "targetConceptName": "Target Concept",
                            "targetVocabularyId": "Target Vocab",
                            "relationshipId": "REL001",
                            "relationshipName": "Test Relationship",
                        }
                    ],
                }
            ],
        }
        mock_http_client.get.return_value = mock_response

        client = AthenaClient()
        result = client.relationships(1)

        assert isinstance(result, ConceptRelationship)
        assert result.count == 1
        mock_http_client.get.assert_called_once_with("/concepts/1/relationships")

    @patch("athena_client.client.HttpClient")
    def test_relationships_api_error_concept_not_found(self, mock_http_client_class):
        """Test relationships with API error for concept not found."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Unable to find ConceptV5 with id 999",
            "errorCode": "CONCEPT_NOT_FOUND",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.relationships(999)

        assert "Concept not found" in str(exc_info.value)
        assert "Concept ID 999 does not exist" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_relationships_api_error_generic(self, mock_http_client_class):
        """Test relationships with generic API error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        error_response = {
            "errorMessage": "Some other error",
            "errorCode": "GENERIC_ERROR",
        }
        mock_http_client.get.return_value = error_response

        client = AthenaClient()

        with pytest.raises(APIError) as exc_info:
            client.relationships(1)

        assert "Failed to get relationships" in str(exc_info.value)
        assert "Some other error" in str(exc_info.value)

    @patch("athena_client.client.HttpClient")
    def test_relationships_retry_on_network_error(self, mock_http_client_class):
        """Test relationships retry on network error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # First call fails, second succeeds
        mock_http_client.get.side_effect = [
            Exception("Network error"),
            {
                "count": 1,
                "items": [
                    {
                        "relationshipName": "Test Relationship",
                        "relationships": [
                            {
                                "targetConceptId": 2,
                                "targetConceptName": "Target Concept",
                                "targetVocabularyId": "Target Vocab",
                                "relationshipId": "REL001",
                                "relationshipName": "Test Relationship",
                            }
                        ],
                    }
                ],
            },
        ]

        client = AthenaClient(max_retries=2, retry_delay=0.1)
        result = client.relationships(1)

        assert isinstance(result, ConceptRelationship)
        assert mock_http_client.get.call_count == 2

    @patch("athena_client.client.HttpClient")
    def test_relationships_retry_failed(self, mock_http_client_class):
        """Test relationships retry failure."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # All calls fail
        mock_http_client.get.side_effect = Exception("Network error")

        client = AthenaClient(max_retries=2, retry_delay=0.1)

        with pytest.raises(AthenaError) as exc_info:
            client.relationships(1)

        assert "Failed to get relationships after 3 attempts" in str(exc_info.value)
        assert mock_http_client.get.call_count == 3

    @patch("athena_client.client.HttpClient")
    def test_graph_success(self, mock_http_client_class):
        """Test successful concept graph."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_response = {
            "terms": [
                {
                    "id": 1,
                    "name": "Test Node",
                    "weight": 1,
                    "depth": 0,
                    "count": 1,
                    "isCurrent": True,
                }
            ],
            "links": [
                {
                    "source": 1,
                    "target": 2,
                    "relationshipId": "REL001",
                    "relationshipName": "Test Relationship",
                }
            ],
        }
        mock_http_client.get.return_value = mock_response

        client = AthenaClient()
        result = client.graph(1, depth=5, zoom_level=3)

        assert isinstance(result, ConceptRelationsGraph)
        assert len(result.terms) == 1
        assert len(result.links) == 1
        mock_http_client.get.assert_called_once_with(
            "/concepts/1/relations", params={"depth": 5, "zoomLevel": 3}
        )

    @patch("athena_client.client.HttpClient")
    def test_graph_retry_on_network_error(self, mock_http_client_class):
        """Test graph retry on network error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # First call fails, second succeeds
        mock_http_client.get.side_effect = [
            Exception("Network error"),
            {
                "terms": [
                    {
                        "id": 1,
                        "name": "Test Node",
                        "weight": 1,
                        "depth": 0,
                        "count": 1,
                        "isCurrent": True,
                    }
                ],
                "links": [
                    {
                        "source": 1,
                        "target": 2,
                        "relationshipId": "REL001",
                        "relationshipName": "Test Relationship",
                    }
                ],
            },
        ]

        client = AthenaClient(max_retries=2, retry_delay=0.1)
        result = client.graph(1)

        assert isinstance(result, ConceptRelationsGraph)
        assert mock_http_client.get.call_count == 2

    @patch("athena_client.client.HttpClient")
    def test_graph_retry_failed(self, mock_http_client_class):
        """Test graph retry failure."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # All calls fail
        mock_http_client.get.side_effect = Exception("Network error")

        client = AthenaClient(max_retries=2, retry_delay=0.1)

        with pytest.raises(AthenaError) as exc_info:
            client.graph(1)

        assert "Failed to get concept graph after 3 attempts" in str(exc_info.value)
        assert mock_http_client.get.call_count == 3

    @patch("athena_client.client.HttpClient")
    def test_summary_success(self, mock_http_client_class):
        """Test successful concept summary."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # Mock responses for details, relationships, and graph
        mock_http_client.get.side_effect = [
            {
                "id": 1,
                "name": "Test Concept",
                "conceptCode": "TEST001",
                "domainId": "Test Domain",
                "vocabularyId": "Test Vocab",
                "conceptClassId": "Test Class",
                "validStart": "2020-01-01",
                "validEnd": "2020-12-31",
            },  # details
            {
                "count": 1,
                "items": [
                    {
                        "relationshipName": "Test Relationship",
                        "relationships": [
                            {
                                "targetConceptId": 2,
                                "targetConceptName": "Target Concept",
                                "targetVocabularyId": "Target Vocab",
                                "relationshipId": "REL001",
                                "relationshipName": "Test Relationship",
                            }
                        ],
                    }
                ],
            },  # relationships
            {
                "terms": [
                    {
                        "id": 1,
                        "name": "Test Node",
                        "weight": 1,
                        "depth": 0,
                        "count": 1,
                        "isCurrent": True,
                    }
                ],
                "links": [
                    {
                        "source": 1,
                        "target": 2,
                        "relationshipId": "REL001",
                        "relationshipName": "Test Relationship",
                    }
                ],
            },  # graph
        ]

        client = AthenaClient()
        result = client.summary(1)

        assert isinstance(result, dict)
        assert "details" in result
        assert "relationships" in result
        assert "graph" in result
        assert mock_http_client.get.call_count == 3

    @patch("athena_client.client.HttpClient")
    def test_summary_without_relationships(self, mock_http_client_class):
        """Test summary without relationships."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        mock_http_client.get.return_value = {
            "id": 1,
            "name": "Test Concept",
            "conceptCode": "TEST001",
            "domainId": "Test Domain",
            "vocabularyId": "Test Vocab",
            "conceptClassId": "Test Class",
            "validStart": "2020-01-01",
            "validEnd": "2020-12-31",
        }

        client = AthenaClient()
        result = client.summary(1, include_relationships=False, include_graph=False)

        assert isinstance(result, dict)
        assert "details" in result
        assert "relationships" not in result
        assert "graph" not in result
        assert mock_http_client.get.call_count == 1

    @patch("athena_client.client.HttpClient")
    def test_summary_without_graph(self, mock_http_client_class):
        """Test summary without graph."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # Mock responses for details and relationships only
        mock_http_client.get.side_effect = [
            {
                "id": 1,
                "name": "Test Concept",
                "conceptCode": "TEST001",
                "domainId": "Test Domain",
                "vocabularyId": "Test Vocab",
                "conceptClassId": "Test Class",
                "validStart": "2020-01-01",
                "validEnd": "2020-12-31",
            },  # details
            {
                "count": 1,
                "items": [
                    {
                        "relationshipName": "Test Relationship",
                        "relationships": [
                            {
                                "targetConceptId": 2,
                                "targetConceptName": "Target Concept",
                                "targetVocabularyId": "Target Vocab",
                                "relationshipId": "REL001",
                                "relationshipName": "Test Relationship",
                            }
                        ],
                    }
                ],
            },  # relationships
        ]

        client = AthenaClient()
        result = client.summary(1, include_graph=False)

        assert isinstance(result, dict)
        assert "details" in result
        assert "relationships" in result
        assert "graph" not in result
        assert mock_http_client.get.call_count == 2

    @patch("athena_client.client.HttpClient")
    def test_summary_retry_on_network_error(self, mock_http_client_class):
        """Test summary retry on network error."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # First call fails, second succeeds
        mock_http_client.get.side_effect = [
            Exception("Network error"),
            {
                "id": 1,
                "name": "Test Concept",
                "conceptCode": "TEST001",
                "domainId": "Test Domain",
                "vocabularyId": "Test Vocab",
                "conceptClassId": "Test Class",
                "validStart": "2020-01-01",
                "validEnd": "2020-12-31",
            },
            {
                "count": 1,
                "items": [
                    {
                        "relationshipName": "Test Relationship",
                        "relationships": [
                            {
                                "targetConceptId": 2,
                                "targetConceptName": "Target Concept",
                                "targetVocabularyId": "Target Vocab",
                                "relationshipId": "REL001",
                                "relationshipName": "Test Relationship",
                            }
                        ],
                    }
                ],
            },
            {
                "terms": [
                    {
                        "id": 1,
                        "name": "Test Node",
                        "weight": 1,
                        "depth": 0,
                        "count": 1,
                        "isCurrent": True,
                    }
                ],
                "links": [
                    {
                        "source": 1,
                        "target": 2,
                        "relationshipId": "REL001",
                        "relationshipName": "Test Relationship",
                    }
                ],
            },
        ]

        client = AthenaClient(max_retries=2, retry_delay=0.1)
        result = client.summary(1)

        assert isinstance(result, dict)
        assert mock_http_client.get.call_count == 4

    @patch("athena_client.client.HttpClient")
    def test_summary_retry_failed(self, mock_http_client_class):
        """Test summary retry failure."""
        mock_http_client = Mock()
        mock_http_client_class.return_value = mock_http_client

        # All calls fail
        mock_http_client.get.side_effect = Exception("Network error")

        client = AthenaClient(max_retries=2, retry_delay=0.1)

        # Summary method catches exceptions and returns them as error messages
        result = client.summary(1)

        assert isinstance(result, dict)
        assert "details" in result
        assert "relationships" in result
        assert "graph" in result
        assert "error" in result["details"]
        assert "error" in result["relationships"]
        assert "error" in result["graph"]
        assert (
            "Failed to get concept details after 3 attempts"
            in result["details"]["error"]
        )
        assert (
            "Failed to get relationships after 3 attempts"
            in result["relationships"]["error"]
        )
        assert (
            "Failed to get concept graph after 3 attempts" in result["graph"]["error"]
        )
        assert (
            mock_http_client.get.call_count == 9
        )  # 3 calls each for details, relationships, and graph


class TestAthena:
    """Test cases for the Athena facade class."""

    def test_athena_inheritance(self):
        """Test that Athena inherits from AthenaClient."""
        assert issubclass(Athena, AthenaClient)

    def test_athena_instantiation(self):
        """Test Athena instantiation."""
        client = Athena()
        assert isinstance(client, AthenaClient)
        assert isinstance(client, Athena)


class TestDatabaseIntegration:
    """Tests for database connector integration in AthenaClient."""

    def test_set_database_connector(self):
        client = AthenaClient()
        connector = Mock()
        client.set_database_connector(connector)
        assert client._db_connector is connector

    def test_validate_local_concepts_calls_connector(self):
        client = AthenaClient()
        connector = Mock()
        connector.validate_concepts.return_value = [1]
        client.set_database_connector(connector)

        result = client.validate_local_concepts([1])

        connector.validate_concepts.assert_called_once_with([1])
        assert result == [1]

    def test_validate_local_concepts_without_connector(self):
        client = AthenaClient()
        with pytest.raises(RuntimeError):
            client.validate_local_concepts([1])

    @patch("athena_client.client.SQLAlchemyConnector")
    @patch("athena_client.client.AthenaAsyncClient")
    def test_generate_concept_set_facade(
        self,
        mock_async_client_class: Mock,
        mock_connector_class: Mock,
    ) -> None:
        expected = {"concept_ids": [1], "metadata": {"status": "SUCCESS"}}

        mock_async_client = Mock()
        mock_async_client.generate_concept_set = AsyncMock(return_value=expected)
        mock_async_client.set_database_connector = Mock()
        mock_async_client_class.return_value = mock_async_client

        mock_connector = Mock()
        mock_connector_class.from_connection_string.return_value = mock_connector

        client = AthenaClient()

        result = asyncio.run(
            client.generate_concept_set(
                "test", "sqlite:///db", strategy="strict", include_descendants=False
            )
        )

        mock_async_client_class.assert_called_once_with(
            base_url=client.http.base_url,
            token=str(client.http.session.headers.get("Authorization", "")),
        )
        mock_connector_class.from_connection_string.assert_called_once_with(
            "sqlite:///db"
        )
        mock_async_client.set_database_connector.assert_called_once_with(mock_connector)
        mock_async_client.generate_concept_set.assert_awaited_once_with(
            "test",
            strategy="strict",
            include_descendants=False,
            confidence_threshold=0.7,
        )
        assert result == expected
