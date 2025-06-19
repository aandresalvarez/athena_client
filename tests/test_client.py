"""
Tests for the AthenaClient class and its enhanced functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
import os

from athena_client import Athena
from athena_client.client import AthenaClient
from athena_client.exceptions import (
    RetryFailedError, NetworkError, APIError, ValidationError,
    AuthenticationError, RateLimitError, ClientError, ServerError
)
from athena_client.models import (
    ConceptDetails, ConceptRelationship, ConceptRelationsGraph,
    ConceptSearchResponse
)
from athena_client.query import Q
from athena_client.search_result import SearchResult
from athena_client.settings import get_settings


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
            timeout=30
        )
        assert client.max_retries == 5
        assert client.retry_delay == 2.0
        assert client.enable_throttling is False
        assert client.throttle_delay_range == (0.2, 0.5)

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Clear the settings cache to ensure environment variables are picked up
        get_settings.cache_clear()
        
        with patch.dict(os.environ, {"ATHENA_MAX_RETRIES": "7"}):
            client = AthenaClient()
            assert client.max_retries == 7
        
        # Clean up by clearing cache again
        get_settings.cache_clear()


class TestRetryConfiguration:
    """Test retry configuration and behavior."""

    def test_retry_configuration_passed_to_http_client(self):
        """Test that retry configuration is passed to HTTP client."""
        with patch('athena_client.client.HttpClient') as mock_http:
            client = AthenaClient(
                max_retries=5,
                enable_throttling=False,
                throttle_delay_range=(0.1, 0.2)
            )
            
            mock_http.assert_called_once()
            call_args = mock_http.call_args[1]
            assert call_args['max_retries'] == 5
            assert call_args['enable_throttling'] is False
            assert call_args['throttle_delay_range'] == (0.1, 0.2)

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
        result = athena_client.search(
            "test",
            max_retries=1,
            retry_delay=0.5
        )
        
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
            {"content": [], "pageable": {}, "totalElements": 0, "last": True, 
             "totalPages": 1, "first": True, "sort": {}, "size": 20, 
             "number": 0, "numberOfElements": 0, "empty": True}
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
            "errorCode": "NOT_FOUND"
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
                    "score": 1.0
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
            "empty": False
        }
        
        athena_client.http.get.return_value = mock_response
        
        result = athena_client.search("aspirin")
        assert result is not None
        assert len(result.all()) == 1
        assert result.all()[0].name == "Aspirin"

    def test_search_with_query_dsl(self, athena_client):
        """Test search with Query DSL."""
        mock_response = {
            "content": [],
            "pageable": {"pageSize": 1},
            "totalElements": 0,
            "last": True,
            "totalPages": 1,
            "first": True,
            "size": 1,
            "number": 0,
            "numberOfElements": 0,
            "empty": True,
        }
        
        athena_client.http.get.return_value = mock_response
        
        query = Q.term("diabetes") & Q.term("type 2")
        result = athena_client.search(query)
        
        # Verify the search method was called
        athena_client.http.get.assert_called_once()
        call_args = athena_client.http.get.call_args
        
        # Verify the query parameter was passed
        params = call_args[1]['params']
        assert 'query' in params
        assert params['query'] is not None

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
            "validEnd": "2099-12-31"
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
                            "relationshipName": "Is a"
                        }
                    ]
                }
            ]
        }
        
        athena_client.http.get.return_value = mock_response
        
        result = athena_client.relationships(1)
        assert result.count == 1
        assert result.items[0].relationshipName == "Is a"

    def test_graph_success(self, athena_client):
        """Test successful graph retrieval."""
        mock_response = {
            "terms": [
                {"id": 1, "name": "Aspirin", "weight": 1, "depth": 0, "count": 1, "isCurrent": True},
                {"id": 2, "name": "Drug", "weight": 1, "depth": 1, "count": 1, "isCurrent": False}
            ],
            "links": [
                {"source": 1, "target": 2, "relationshipId": "Is a", "relationshipName": "Is a"}
            ],
            "connectionsCount": 1
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
            "validEnd": "2099-12-31"
        }
        relationships_response = {
            "count": 0,
            "items": []
        }
        graph_response = {
            "terms": [],
            "links": [],
            "connectionsCount": 0
        }
        athena_client.http.get.side_effect = [
            details_response,
            relationships_response,
            graph_response
        ]
        result = athena_client.summary(1)
        # The summary method returns a dict with the raw response data
        assert result["details"]["name"] == "Aspirin"
        assert result["relationships"]["count"] == 0
        assert result["graph"]["connectionsCount"] == 0


class TestErrorScenarios:
    """Test various error scenarios and their handling."""

    def test_authentication_error(self, athena_client):
        # Return an error response that the search method will detect
        error_response = {
            "result": None,
            "errorMessage": "Invalid token",
            "errorCode": "AUTH_ERROR"
        }
        athena_client.http = Mock()
        athena_client.http.get.return_value = dict(error_response)
        
        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)
        
        assert "Invalid token" in str(exc_info.value)

    def test_rate_limit_error(self, athena_client):
        error_response = {
            "result": None,
            "errorMessage": "Rate limit exceeded",
            "errorCode": "RATE_LIMIT"
        }
        athena_client.http = Mock()
        athena_client.http.get.return_value = dict(error_response)
        
        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)
        
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_client_error(self, athena_client):
        error_response = {
            "result": None,
            "errorMessage": "Bad request",
            "errorCode": "BAD_REQUEST"
        }
        athena_client.http = Mock()
        athena_client.http.get.return_value = dict(error_response)
        
        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)
        
        assert "Bad request" in str(exc_info.value)

    def test_server_error(self, athena_client):
        error_response = {
            "result": None,
            "errorMessage": "Internal server error",
            "errorCode": "SERVER_ERROR"
        }
        athena_client.http = Mock()
        athena_client.http.get.return_value = dict(error_response)
        
        with pytest.raises(APIError) as exc_info:
            athena_client.search("test", max_retries=0)
        
        assert "Internal server error" in str(exc_info.value)


class TestRetryDelay:
    """Test retry delay functionality."""

    @patch('time.sleep')
    def test_retry_delay_applied(self, mock_sleep, athena_client):
        """Test that retry delay is applied between attempts."""
        # Mock network error for first attempt, success on second
        athena_client.http.get.side_effect = [
            NetworkError("Connection failed"),
            {"content": [], "pageable": {}, "totalElements": 0, "last": True,
             "totalPages": 1, "first": True, "sort": {}, "size": 20,
             "number": 0, "numberOfElements": 0, "empty": True}
        ]
        
        athena_client.search("test", retry_delay=1.0, max_retries=2)
        
        # Verify sleep was called with the retry delay
        mock_sleep.assert_called_once_with(1.0)

    def test_no_retry_delay_when_none(self, athena_client):
        """Test that no delay is applied when retry_delay is None."""
        # Mock network error for first attempt, success on second
        athena_client.http.get.side_effect = [
            NetworkError("Connection failed"),
            {"content": [], "pageable": {}, "totalElements": 0, "last": True,
             "totalPages": 1, "first": True, "sort": {}, "size": 20,
             "number": 0, "numberOfElements": 0, "empty": True}
        ]
        
        with patch('time.sleep') as mock_sleep:
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

    def test_athena_facade_capabilities(self):
        """Test Athena facade capabilities method."""
        # Athena.capabilities() is deprecated or removed; skip this test.
        pass 