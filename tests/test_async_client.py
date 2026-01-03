"""Tests for the async client module."""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import orjson
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
    async def test_default_headers_include_browser_like_fields(self):
        """Async client should include Referer and Accept-Language headers."""
        client = AsyncHttpClient()
        headers = client._setup_default_headers()
        assert "Referer" in headers
        assert headers["Referer"].startswith("https://athena.ohdsi.org/")
        assert "Accept-Language" in headers
        assert "User-Agent" in headers

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
        response.content = orjson.dumps({"result": "success"})

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
        mock_response.content = orjson.dumps({"result": "success"})

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.request("GET", "/test")
            assert result == {"result": "success"}

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_merges_auth_and_default_headers(self, mock_build_headers):
        """Request should merge auth headers with default browser-like headers."""
        mock_build_headers.return_value = {"X-Athena-Auth": "Bearer token-123"}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = orjson.dumps({"ok": True})

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_request:
            await client.request("GET", "/concepts", params={"query": "x"})
            called_headers = mock_request.call_args[1]["headers"]
            # Auth header present
            assert called_headers["X-Athena-Auth"] == "Bearer token-123"
            # Default headers present
            assert called_headers["Referer"].startswith("https://athena.ohdsi.org/")
            assert "User-Agent" in called_headers

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_with_params(self, mock_build_headers):
        """Test request with parameters."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = orjson.dumps({"result": "success"})

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
        mock_response.content = orjson.dumps({"result": "success"})

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_request:
            await client.request("POST", "/test", data={"key": "value"})
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["content"] == b'{"key":"value"}'

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_includes_security_headers(
        self, mock_build_headers: Mock
    ) -> None:
        """Security headers should be sent on actual requests."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = orjson.dumps({"result": "success"})
        mock_response.reason_phrase = "OK"

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_request:
            await client.request("GET", "/test")
            call_headers = mock_request.call_args[1]["headers"]
            normalized_headers = {key.lower(): value for key, value in call_headers.items()}
            assert normalized_headers["accept"] == "application/json, text/plain, */*"
            assert normalized_headers["origin"] == "https://athena.ohdsi.org"
            assert normalized_headers["sec-fetch-site"] == "same-origin"
            assert normalized_headers["sec-fetch-mode"] == "cors"
            assert normalized_headers["sec-fetch-dest"] == "empty"

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_headers_omit_content_type_for_get(
        self, mock_build_headers: Mock
    ) -> None:
        """GET requests should not set Content-Type."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.content = orjson.dumps({"result": "success"})
        mock_response.reason_phrase = "OK"

        with patch.object(
            client.client, "request", new_callable=AsyncMock, return_value=mock_response
        ) as mock_request:
            await client.request("GET", "/test")
            call_headers = mock_request.call_args[1]["headers"]
            assert "Content-Type" not in call_headers

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_waf_403_html_retry_regression(
        self, mock_build_headers: Mock
    ) -> None:
        """Regression test for issue #15: HTML 403 should trigger UA fallback."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        first_response = Mock()
        first_response.status_code = 403
        first_response.headers = {"Content-Type": "text/html"}
        first_response.text = "<html>Forbidden</html>"
        first_response.reason_phrase = "Forbidden"

        second_response = Mock()
        second_response.status_code = 200
        second_response.headers = {"Content-Type": "application/json"}
        second_response.content = orjson.dumps({"result": "success"})
        second_response.reason_phrase = "OK"

        with patch.object(client, "_USER_AGENTS", ["agent1", "agent2"]):
            with patch.object(
                client.client,
                "request",
                new_callable=AsyncMock,
                side_effect=[first_response, second_response],
            ) as mock_request:
                result = await client.request("GET", "/test")
                assert result == {"result": "success"}
                assert mock_request.call_count == 2
                retry_headers = mock_request.call_args_list[1][1]["headers"]
                normalized_headers = {key.lower(): value for key, value in retry_headers.items()}
                assert normalized_headers["origin"] == "https://athena.ohdsi.org"
                assert normalized_headers["sec-fetch-site"] == "same-origin"
                assert "content-type" not in normalized_headers

    @patch("athena_client.async_client.build_headers")
    @pytest.mark.asyncio
    async def test_request_retry_preserves_content_type_for_body(
        self, mock_build_headers: Mock
    ) -> None:
        """Fallback retries should retain Content-Type for requests with a body."""
        mock_build_headers.return_value = {}

        client = AsyncHttpClient()
        first_response = Mock()
        first_response.status_code = 403
        first_response.headers = {"Content-Type": "text/html"}
        first_response.text = "blocked"
        first_response.reason_phrase = "Forbidden"

        second_response = Mock()
        second_response.status_code = 200
        second_response.headers = {"Content-Type": "application/json"}
        second_response.content = orjson.dumps({"result": "success"})
        second_response.reason_phrase = "OK"

        with patch.object(client, "_USER_AGENTS", ["agent1", "agent2"]):
            with patch.object(
                client.client,
                "request",
                new_callable=AsyncMock,
                side_effect=[first_response, second_response],
            ) as mock_request:
                result = await client.request("POST", "/test", data={"key": "value"})
                assert result == {"result": "success"}
                retry_headers = mock_request.call_args_list[1][1]["headers"]
                assert retry_headers["Content-Type"] == "application/json"

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
    async def test_get_method_with_timeout(self) -> None:
        """Test GET method with a timeout override."""
        client = AsyncHttpClient()

        with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"result": "success"}
            await client.get("/test", params={"key": "value"}, timeout=10)
            mock_request.assert_called_once_with(
                "GET",
                "/test",
                params={"key": "value"},
                raw_response=False,
                timeout=10,
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
    async def test_post_method_with_timeout(self) -> None:
        """Test POST method with a timeout override."""
        client = AsyncHttpClient()

        with patch.object(client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = {"result": "success"}
            await client.post("/test", data={"key": "value"}, timeout=10)
            mock_request.assert_called_once_with(
                "POST",
                "/test",
                data={"key": "value"},
                params=None,
                raw_response=False,
                timeout=10,
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

    @pytest.mark.asyncio
    async def test_async_http_client_header_race_condition_regression(self):
        """
        Regression test: Concurrent requests should not interfere with each other's 
        headers when one triggers a User-Agent rotation.
        """
        client = AsyncHttpClient()
        
        # Mock responses distinguishing requests by path
        resp_403 = Mock(spec=httpx.Response)
        resp_403.status_code = 403
        resp_403.headers = {"Content-Type": "text/html"}
        resp_403.text = "Forbidden"
        resp_403.reason_phrase = "Forbidden"
        
        resp_200 = Mock(spec=httpx.Response)
        resp_200.status_code = 200
        resp_200.headers = {"Content-Type": "application/json"}
        resp_200.content = orjson.dumps({"ok": True})
        resp_200.reason_phrase = "OK"
        
        # Mock the method that constructs headers
        def mock_setup_headers(user_agent_idx=0):
            return {
                "User-Agent": f"UA{user_agent_idx + 1}",
                "Origin": "https://athena.ohdsi.org",
                "Sec-Fetch-Site": "same-origin",
            }
        
        client._setup_default_headers = mock_setup_headers
        
        with patch.object(client, "_USER_AGENTS", ["UA1", "UA2"]):
            with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
                # We want to simulate Request 1 and Request 2 happening concurrently.
                # Request 1 will call request() twice (due to 403 retry).
                # Request 2 will call request() once.
                
                # Setup side effect to return 403 for /req1 first time, then 200
                async def side_effect(method, url, **kwargs):
                    if "/req1" in url:
                        if not hasattr(side_effect, "req1_called"):
                            side_effect.req1_called = True
                            return resp_403
                        return resp_200
                    return resp_200
                
                mock_request.side_effect = side_effect
                
                # Run both concurrently
                import asyncio
                task1 = asyncio.create_task(client.request("GET", "/req1"))
                task2 = asyncio.create_task(client.request("GET", "/req2"))
                
                await asyncio.gather(task1, task2)
                
                # Verify headers for each call
                for call in mock_request.call_args_list:
                    args, kwargs = call
                    url = kwargs["url"]
                    ua = kwargs["headers"]["User-Agent"]
                    
                    if "/req2" in url:
                        # Request 2 should ALWAYS have UA1 because it never retried
                        assert ua == "UA1", f"Request 2 used wrong UA: {ua}"
                    elif "/req1" in url:
                        # Request 1 should have UA1 on first call and UA2 on second
                        pass # We already verified this implicitly by checking all calls
                
                # Check req1 specifically
                req1_calls = [c for c in mock_request.call_args_list if "/req1" in c[1]["url"]]
                assert len(req1_calls) == 2
                assert req1_calls[0][1]["headers"]["User-Agent"] == "UA1"
                assert req1_calls[1][1]["headers"]["User-Agent"] == "UA2"

    @pytest.mark.asyncio
    async def test_search_uses_dynamic_timeout_regression(self):
        """
        Regression test: search should calculate and use a dynamic timeout
        if none is provided.
        """
        client = AthenaAsyncClient()
        mock_response = {
            "content": [],
            "totalElements": 0,
            "totalPages": 0,
            "pageable": {"pageSize": 20, "pageNumber": 0},
        }
        
        # Patch where it's defined - athena_client.utils.get_operation_timeout
        with patch("athena_client.utils.get_operation_timeout", return_value=123) as mock_get_timeout:
            with patch.object(client, "search_concepts", new_callable=AsyncMock, return_value=mock_response) as mock_search:
                await client.search("aspirin")
                
                # Verify timeout was calculated
                mock_get_timeout.assert_called_once()
                # Verify search_concepts was called with the calculated timeout
                assert mock_search.call_args[1]["timeout"] == 123
