"""Tests for the async client module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from athena_client.async_client import AsyncHttpClient, AthenaAsyncClient
from athena_client.exceptions import AthenaError, ClientError, NetworkError, ServerError
from athena_client.models import (
    ConceptDetails,
    ConceptRelationsGraph,
    ConceptRelationship,
)


class TestAsyncHttpClient:
    """Test cases for the AsyncHttpClient class."""

    @pytest.mark.asyncio
    async def test_init_with_defaults(self):
        """Test AsyncHttpClient initialization with default values."""
        with patch("athena_client.async_client.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_BASE_URL = "https://api.example.com"
            mock_settings.ATHENA_TIMEOUT_SECONDS = 30
            mock_settings.ATHENA_MAX_RETRIES = 3
            mock_settings.ATHENA_BACKOFF_FACTOR = 0.3
            mock_get_settings.return_value = mock_settings

            client = AsyncHttpClient()

            assert client.base_url == "https://api.example.com"
            assert client.timeout == 30
            assert client.max_retries == 3
            assert client.backoff_factor == 0.3

    @pytest.mark.asyncio
    async def test_init_with_custom_values(self):
        """Test AsyncHttpClient initialization with custom values."""
        client = AsyncHttpClient(
            base_url="https://custom.api.com",
            token="test-token",
            timeout=60,
            max_retries=5,
            backoff_factor=0.5,
        )

        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.backoff_factor == 0.5

    @pytest.mark.asyncio
    async def test_build_url(self):
        """Test URL building."""
        client = AsyncHttpClient(base_url="https://api.example.com")
        url = client._build_url("/concepts/search")
        assert url == "https://api.example.com/concepts/search"

    @pytest.mark.asyncio
    async def test_handle_response_success(self):
        """Test successful response handling."""
        client = AsyncHttpClient()
        response = Mock()
        response.json.return_value = {"result": "success"}

        result = await client._handle_response(response)
        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_handle_response_client_error(self):
        """Test client error response handling."""
        client = AsyncHttpClient()
        response = Mock()
        response.status_code = 400
        response.reason_phrase = "Bad Request"
        response.text = "Invalid request"
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400 Bad Request", request=Mock(), response=response
        )

        with pytest.raises(ClientError) as exc_info:
            await client._handle_response(response)
        assert "400 Bad Request" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_response_server_error(self):
        """Test server error response handling."""
        client = AsyncHttpClient()
        response = Mock()
        response.status_code = 500
        response.reason_phrase = "Internal Server Error"
        response.text = "Server error"
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=Mock(), response=response
        )

        with pytest.raises(ServerError) as exc_info:
            await client._handle_response(response)
        assert "500 Internal Server Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_response_decoding_error(self):
        """Test JSON decoding error handling."""
        client = AsyncHttpClient()
        response = Mock()
        response.raise_for_status.side_effect = httpx.DecodingError("Invalid JSON")

        with pytest.raises(AthenaError) as exc_info:
            await client._handle_response(response)

        assert "Invalid JSON" in str(exc_info.value)

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_success(self, mock_build_headers):
        """Test successful request."""
        mock_build_headers.return_value = {"Authorization": "Bearer token"}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.request("GET", "/test")
            assert result == {"result": "success"}

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_with_params(self, mock_build_headers):
        """Test request with parameters."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_request:
            await client.request("GET", "/test", params={"key": "value"})
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["params"] == {"key": "value"}

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_with_data(self, mock_build_headers):
        """Test request with data."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_request:
            await client.request("POST", "/test", data={"key": "value"})
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["content"] == b'{"key": "value"}'

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_raw_response(self, mock_build_headers):
        """Test request with raw response."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.request("GET", "/test", raw_response=True)
            assert result == mock_response

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_timeout_error(self, mock_build_headers):
        """Test request with timeout error."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()

        with patch.object(
            client.client,
            "request",
            new_callable=AsyncMock,
            side_effect=httpx.TimeoutException("Request timeout"),
        ):
            with pytest.raises(NetworkError) as exc_info:
                await client.request("GET", "/test")
            assert "Request timeout" in str(exc_info.value)

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_connect_error(self, mock_build_headers):
        """Test request with connection error."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()

        with patch.object(
            client.client,
            "request",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection failed"),
        ):
            with pytest.raises(NetworkError) as exc_info:
                await client.request("GET", "/test")
            assert "Connection failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_method(self):
        """Test GET method."""
        client = AsyncHttpClient()

        with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"result": "success"}
            await client.get("/test", params={"key": "value"})
            mock_request.assert_called_once_with(
                "GET", "/test", params={"key": "value"}, raw_response=False
            )

    @pytest.mark.asyncio
    async def test_post_method(self):
        """Test POST method."""
        client = AsyncHttpClient()

        with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"result": "success"}
            await client.post("/test", data={"key": "value"})
            mock_request.assert_called_once_with(
                "POST", "/test", data={"key": "value"}, params=None, raw_response=False
            )

    @pytest.mark.asyncio
    async def test_backoff_import_error(self):
        """Test that import error is raised when backoff is not available."""
        # Clear the module cache to force re-import
        import sys

        if "athena_client.async_client" in sys.modules:
            del sys.modules["athena_client.async_client"]

        with patch.dict("sys.modules", {"backoff": None}):
            with pytest.raises(
                ImportError, match="backoff is required for the async client"
            ):
                import importlib

                importlib.import_module("athena_client.async_client")


class TestAthenaAsyncClient:
    """Test cases for the AthenaAsyncClient class."""

    @pytest.mark.asyncio
    async def test_init(self):
        """Test AthenaAsyncClient initialization."""
        client = AthenaAsyncClient(
            base_url="https://api.example.com",
            token="test-token",
            timeout=60,
        )

        assert client.http.base_url == "https://api.example.com"

    @pytest.mark.asyncio
    async def test_search_concepts(self):
        """Test search_concepts method."""
        client = AthenaAsyncClient()
        mock_response = {
            "content": [{"id": 1, "name": "Test Concept"}],
            "totalElements": 1,
            "totalPages": 1,
        }

        with patch.object(
            client.http, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.search_concepts("test query")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_search_concepts_with_filters(self):
        """Test search_concepts method with filters."""
        client = AthenaAsyncClient()
        mock_response = {"content": [], "totalElements": 0}

        with patch.object(
            client.http, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            await client.search_concepts(
                query="test",
                domain="Condition",
                vocabulary="SNOMED",
                standard_concept="S",
                page_size=50,
                page=1,
            )

    @pytest.mark.asyncio
    async def test_get_concept_details(self):
        """Test get_concept_details method."""
        client = AthenaAsyncClient()
        mock_response = {
            "id": 1,
            "name": "Test Concept",
            "domainId": "Condition",
            "vocabularyId": "SNOMED",
            "conceptClassId": "Clinical Finding",
            "conceptCode": "TEST001",
            "validStart": "2020-01-01",
            "validEnd": "2099-12-31",
            "vocabulary": {"name": "Test Vocab"},
            "domain": {"name": "Test Domain"},
        }

        with patch.object(
            client.http, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.get_concept_details(1)
            assert isinstance(result, ConceptDetails)
            assert result.id == 1
            assert result.name == "Test Concept"

    @pytest.mark.asyncio
    async def test_get_concept_relationships(self):
        """Test get_concept_relationships method."""
        client = AthenaAsyncClient()
        mock_response = {
            "count": 1,
            "items": [
                {
                    "relationshipName": "Is a",
                    "relationships": [
                        {
                            "targetConceptId": 2,
                            "targetConceptName": "Test Target",
                            "targetVocabularyId": "SNOMED",
                            "relationshipId": "Is a",
                            "relationshipName": "Is a",
                        }
                    ],
                }
            ],
        }

        with patch.object(
            client.http, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.get_concept_relationships(1)
            assert isinstance(result, ConceptRelationship)
            assert result.count == 1

    @pytest.mark.asyncio
    async def test_get_concept_relationships_with_filters(self):
        """Test get_concept_relationships method with filters."""
        client = AthenaAsyncClient()
        mock_response = {"count": 0, "items": []}

        with patch.object(
            client.http, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.get_concept_relationships(
                1,
                relationship_id="Is a",
                only_standard=True,
            )
            assert isinstance(result, ConceptRelationship)
            assert result.count == 0

    @pytest.mark.asyncio
    async def test_get_concept_graph(self):
        """Test get_concept_graph method."""
        client = AthenaAsyncClient()
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
                    "relationshipId": "Is a",
                    "relationshipName": "Is a",
                }
            ],
        }

        with patch.object(
            client.http, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.get_concept_graph(1, depth=5, zoom_level=3)
            assert isinstance(result, ConceptRelationsGraph)
            assert len(result.terms) == 1
            assert len(result.links) == 1

    @pytest.mark.asyncio
    async def test_httpx_import_error(self):
        """Test that AttributeError is raised when httpx is not available."""
        # Clear the module cache to force re-import
        import sys

        if "athena_client.async_client" in sys.modules:
            del sys.modules["athena_client.async_client"]

        with patch.dict("sys.modules", {"httpx": None}):
            with pytest.raises(
                AttributeError, match="httpx is required for the async client"
            ):
                import importlib

                importlib.import_module("athena_client.async_client")

    @pytest.mark.asyncio
    async def test_generate_concept_set_without_db(self):
        client = AthenaAsyncClient()

        with pytest.raises(RuntimeError):
            await client.generate_concept_set("test")
