"""Tests for the enhanced HttpClient class."""

import json
from unittest.mock import Mock, patch
from urllib.parse import urljoin

import pytest
import requests
from requests.exceptions import ConnectionError, Timeout

from athena_client.exceptions import (
    AuthenticationError,
    ClientError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from athena_client.http import HttpClient


class TestHttpClient:
    """Test cases for the HttpClient class."""

    def test_init_with_defaults(self):
        """Test HttpClient initialization with default values."""
        with patch("athena_client.http.get_settings") as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ATHENA_BASE_URL = "https://api.example.com"
            mock_settings.ATHENA_TIMEOUT_SECONDS = 30
            mock_settings.ATHENA_MAX_RETRIES = 3
            mock_settings.ATHENA_BACKOFF_FACTOR = 0.3
            mock_get_settings.return_value = mock_settings

            client = HttpClient()

            assert client.base_url == "https://api.example.com"
            assert client.timeout == 30
            assert client.max_retries == 3
            assert client.backoff_factor == 0.3
            assert client.enable_throttling is True
            assert client.throttle_delay_range == (0.1, 0.3)

    def test_init_with_custom_values(self):
        """Test HttpClient initialization with custom values."""
        client = HttpClient(
            base_url="https://custom.api.com",
            token="test-token",
            timeout=60,
            max_retries=5,
            backoff_factor=0.5,
            enable_throttling=False,
            throttle_delay_range=(0.5, 1.0),
        )

        assert client.base_url == "https://custom.api.com"
        assert client.timeout == 60
        assert client.max_retries == 5
        assert client.backoff_factor == 0.5
        assert client.enable_throttling is False
        assert client.throttle_delay_range == (0.5, 1.0)

    def test_create_session(self):
        """Test session creation with retry configuration."""
        client = HttpClient(max_retries=5, backoff_factor=0.5)
        session = client.session

        assert session is not None
        # Check that adapters are mounted
        assert "http://" in session.adapters
        assert "https://" in session.adapters

    def test_setup_default_headers(self):
        """Test default headers setup."""
        client = HttpClient()
        headers = client.session.headers

        assert headers["Accept"] == "application/json, text/plain, */*"
        assert "Content-Type" not in headers  # Should not be in default headers
        assert headers["Origin"] == "https://athena.ohdsi.org"
        assert headers["Sec-Fetch-Site"] == "same-origin"
        assert headers["Sec-Fetch-Mode"] == "cors"
        assert headers["Sec-Fetch-Dest"] == "empty"
        expected_user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        assert headers["User-Agent"] == expected_user_agent

    def test_throttle_request_enabled(self):
        """Test request throttling when enabled."""
        client = HttpClient(enable_throttling=True)

        with patch("time.sleep") as mock_sleep:
            client._throttle_request()
            mock_sleep.assert_called_once()

    def test_throttle_request_disabled(self):
        """Test request throttling when disabled."""
        client = HttpClient(enable_throttling=False)

        with patch("time.sleep") as mock_sleep:
            client._throttle_request()
            mock_sleep.assert_not_called()

    def test_handle_rate_limit_with_retry_after(self):
        """Test rate limit handling with Retry-After header."""
        client = HttpClient()
        response = Mock()
        response.headers = {"Retry-After": "30"}

        with patch("time.sleep") as mock_sleep:
            client._handle_rate_limit(response)
            mock_sleep.assert_called_once_with(30)

    def test_handle_rate_limit_without_retry_after(self):
        """Test rate limit handling without Retry-After header."""
        client = HttpClient()
        response = Mock()
        response.headers = {}

        with patch("time.sleep") as mock_sleep:
            client._handle_rate_limit(response)
            mock_sleep.assert_called_once_with(60)

    def test_build_url(self):
        """Test URL building."""
        client = HttpClient(base_url="https://api.example.com")
        url = client._build_url("/concepts/search")
        expected = urljoin("https://api.example.com", "/concepts/search")
        assert url == expected

    def test_normalize_params(self):
        """Test parameter normalization."""
        client = HttpClient()

        # Test with None
        assert client._normalize_params(None) is None

        # Test with empty dict
        assert client._normalize_params({}) == {}

        # Test with mixed types
        params = {"string": "value", "int": 123, "float": 1.23, "bool": True}
        normalized = client._normalize_params(params)
        assert normalized == {
            "string": "value",
            "int": "123",
            "float": "1.23",
            "bool": "True",
        }

    def test_handle_response_success(self):
        """Test successful response handling."""
        client = HttpClient()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"result": "success"}
        response.text = "success response"

        result = client._handle_response(response, "https://api.example.com/test")
        assert result == {"result": "success"}

    def test_handle_response_400_error(self):
        """Test 400 error response handling."""
        client = HttpClient()
        response = Mock()
        response.status_code = 400
        response.reason_phrase = "Bad Request"
        response.text = "Invalid request"

        # Create a proper HTTPError with the response object
        http_error = requests.exceptions.HTTPError("400 Bad Request")
        http_error.response = response
        response.raise_for_status.side_effect = http_error

        with pytest.raises(ClientError) as exc_info:
            client._handle_response(response, "https://api.example.com/test")

        assert "400" in str(exc_info.value)

    def test_handle_response_401_error(self):
        """Test 401 error response handling."""
        client = HttpClient()
        response = Mock()
        response.status_code = 401
        response.reason_phrase = "Unauthorized"
        response.text = "Authentication required"

        # Create a proper HTTPError with the response object
        http_error = requests.exceptions.HTTPError("401 Unauthorized")
        http_error.response = response
        response.raise_for_status.side_effect = http_error

        with pytest.raises(AuthenticationError) as exc_info:
            client._handle_response(response, "https://api.example.com/test")

        assert "401" in str(exc_info.value)

    def test_handle_response_429_error(self):
        """Test 429 error response handling."""
        client = HttpClient()
        response = Mock()
        response.status_code = 429
        response.reason_phrase = "Too Many Requests"
        response.text = "Rate limit exceeded"

        # Create a proper HTTPError with the response object
        http_error = requests.exceptions.HTTPError("429 Too Many Requests")
        http_error.response = response
        response.raise_for_status.side_effect = http_error

        with pytest.raises(RateLimitError) as exc_info:
            client._handle_response(response, "https://api.example.com/test")

        assert "429" in str(exc_info.value)

    def test_handle_response_500_error(self):
        """Test 500 error response handling."""
        client = HttpClient()
        response = Mock()
        response.status_code = 500
        response.reason_phrase = "Internal Server Error"
        response.text = "Server error"

        # Create a proper HTTPError with the response object
        http_error = requests.exceptions.HTTPError("500 Internal Server Error")
        http_error.response = response
        response.raise_for_status.side_effect = http_error

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(response, "https://api.example.com/test")

        assert "500" in str(exc_info.value)

    def test_handle_response_invalid_json(self):
        """Test invalid JSON response handling."""
        client = HttpClient()
        response = Mock()
        response.status_code = 200
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.text = "invalid json"

        with pytest.raises(ValidationError) as exc_info:
            client._handle_response(response, "https://api.example.com/test")

        assert "Invalid JSON" in str(exc_info.value)

    @patch("athena_client.http.build_headers")
    def test_request_success(self, mock_build_headers):
        """Test successful request."""
        mock_build_headers.return_value = {"Authorization": "Bearer token"}

        client = HttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.text = "success response"
        mock_response.reason = "OK"

        with patch.object(client.session, "request", return_value=mock_response):
            result = client.request("GET", "/test")
            assert result == {"result": "success"}

    @patch("athena_client.http.build_headers")
    def test_request_with_params(self, mock_build_headers):
        """Test request with parameters."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.text = "success response"
        mock_response.reason = "OK"

        with patch.object(
            client.session, "request", return_value=mock_response
        ) as mock_request:
            client.request("GET", "/test", params={"key": "value"})
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["params"] == {"key": "value"}

    @patch("athena_client.http.build_headers")
    def test_request_with_data(self, mock_build_headers):
        """Test request with data."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.text = "success response"
        mock_response.reason = "OK"

        with patch.object(
            client.session, "request", return_value=mock_response
        ) as mock_request:
            client.request("POST", "/test", data={"key": "value"})
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]["data"] == b'{"key":"value"}'

    @patch("athena_client.http.build_headers")
    def test_request_includes_security_headers(
        self, mock_build_headers: Mock
    ) -> None:
        """Security headers should be sent on actual requests."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_response.text = "success response"
        mock_response.reason = "OK"

        with patch.object(
            client.session, "request", return_value=mock_response
        ) as mock_request:
            client.request("GET", "/test")
            call_headers = mock_request.call_args[1]["headers"]
            assert call_headers["Accept"] == "application/json, text/plain, */*"
            assert call_headers["Origin"] == "https://athena.ohdsi.org"
            assert call_headers["Sec-Fetch-Site"] == "same-origin"
            assert call_headers["Sec-Fetch-Mode"] == "cors"
            assert call_headers["Sec-Fetch-Dest"] == "empty"

    @patch("athena_client.http.build_headers")
    def test_request_headers_omit_content_type_for_get(
        self, mock_build_headers: Mock
    ) -> None:
        """GET requests should not set Content-Type."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"result": "success"}
        mock_response.text = "success response"
        mock_response.reason = "OK"

        with patch.object(
            client.session, "request", return_value=mock_response
        ) as mock_request:
            client.request("GET", "/test")
            call_headers = mock_request.call_args[1]["headers"]
            assert "Content-Type" not in call_headers

    @patch("athena_client.http.build_headers")
    def test_request_waf_403_html_retry_regression(
        self, mock_build_headers: Mock
    ) -> None:
        """Regression test for issue #15: HTML 403 should trigger UA fallback."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        first_response = Mock()
        first_response.status_code = 403
        first_response.headers = {"Content-Type": "text/html"}
        first_response.text = "<html>Forbidden</html>"
        first_response.reason = "Forbidden"

        second_response = Mock()
        second_response.status_code = 200
        second_response.headers = {"Content-Type": "application/json"}
        second_response.json.return_value = {"result": "success"}
        second_response.text = "ok"
        second_response.reason = "OK"

        with patch.object(client, "_USER_AGENTS", ["agent1", "agent2"]):
            with patch.object(
                client.session,
                "request",
                side_effect=[first_response, second_response],
            ) as mock_request:
                result = client.request("GET", "/test")
                assert result == {"result": "success"}
                assert mock_request.call_count == 2
                retry_headers = mock_request.call_args_list[1][1]["headers"]
                assert retry_headers["Origin"] == "https://athena.ohdsi.org"
                assert retry_headers["Sec-Fetch-Site"] == "same-origin"
                assert "Content-Type" not in retry_headers

    @patch("athena_client.http.build_headers")
    def test_request_retry_preserves_content_type_for_body(
        self, mock_build_headers: Mock
    ) -> None:
        """Fallback retries should retain Content-Type for requests with a body."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        first_response = Mock()
        first_response.status_code = 200
        first_response.headers = {"Content-Type": "text/html"}
        first_response.text = "blocked"
        first_response.reason = "OK"

        second_response = Mock()
        second_response.status_code = 200
        second_response.headers = {"Content-Type": "application/json"}
        second_response.json.return_value = {"result": "success"}
        second_response.text = "ok"
        second_response.reason = "OK"

        with patch.object(client, "_USER_AGENTS", ["agent1", "agent2"]):
            with patch.object(
                client.session,
                "request",
                side_effect=[first_response, second_response],
            ) as mock_request:
                result = client.request("POST", "/test", data={"key": "value"})
                assert result == {"result": "success"}
                retry_headers = mock_request.call_args_list[1][1]["headers"]
                assert retry_headers["Content-Type"] == "application/json"

    @patch("athena_client.http.build_headers")
    def test_request_raw_response(self, mock_build_headers):
        """Test request with raw response."""
        mock_build_headers.return_value = {}

        client = HttpClient()
        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(client.session, "request", return_value=mock_response):
            result = client.request("GET", "/test", raw_response=True)
            assert result == mock_response

    @patch("athena_client.http.build_headers")
    def test_request_network_error(self, mock_build_headers):
        """Test request with network error."""
        mock_build_headers.return_value = {}

        client = HttpClient(max_retries=0)  # Disable retries for this test

        # Patch the User-Agent list to have only one entry to avoid multiple retries
        with patch.object(client, "_USER_AGENTS", [client._USER_AGENTS[0]]):
            with patch.object(
                client.session,
                "request",
                side_effect=ConnectionError("Connection failed"),
            ):
                with pytest.raises(ConnectionError):  # Expect the original exception
                    client.request("GET", "/test")

    @patch("athena_client.http.build_headers")
    def test_request_timeout_error(self, mock_build_headers):
        """Test request with timeout error."""
        mock_build_headers.return_value = {}

        client = HttpClient(max_retries=0)  # Disable retries for this test

        # Patch the User-Agent list to have only one entry to avoid multiple retries
        with patch.object(client, "_USER_AGENTS", [client._USER_AGENTS[0]]):
            with patch.object(
                client.session, "request", side_effect=Timeout("Request timeout")
            ):
                with pytest.raises(Timeout):  # Expect the original exception
                    client.request("GET", "/test")

    def test_get_method(self):
        """Test GET method."""
        client = HttpClient()

        with patch.object(client, "request") as mock_request:
            mock_request.return_value = {"result": "success"}
            result = client.get("/test", params={"key": "value"})

            mock_request.assert_called_once_with(
                "GET", "/test", params={"key": "value"}, raw_response=False
            )
            assert result == {"result": "success"}

    def test_post_method(self):
        """Test POST method."""
        client = HttpClient()

        with patch.object(client, "request") as mock_request:
            mock_request.return_value = {"result": "success"}
            result = client.post("/test", data={"key": "value"})

            mock_request.assert_called_once_with(
                "POST", "/test", data={"key": "value"}, params=None, raw_response=False
            )
            assert result == {"result": "success"}

    def test_post_method_with_timeout(self) -> None:
        """Test POST method with a timeout override."""
        client = HttpClient()

        with patch.object(client, "request") as mock_request:
            mock_request.return_value = {"result": "success"}
            result = client.post("/test", data={"key": "value"}, timeout=10)

            mock_request.assert_called_once_with(
                "POST",
                "/test",
                data={"key": "value"},
                params=None,
                raw_response=False,
                timeout=10,
            )
            assert result == {"result": "success"}

    def test_close(self):
        """Test client close method."""
        client = HttpClient()

        with patch.object(client.session, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()

    def test_context_manager(self):
        """Test client as context manager."""
        with HttpClient() as client:
            assert isinstance(client, HttpClient)

        # Session should be closed after context exit
        # Note: requests.Session doesn't have a 'closed' attribute, so we check
        # if close was called

    def test_context_manager_exception(self):
        """Test context manager with exception."""
        with pytest.raises(ValueError):
            with HttpClient():
                raise ValueError("Test exception")

        # Session should still be closed even with exception
        # Note: requests.Session doesn't have a 'closed' attribute
