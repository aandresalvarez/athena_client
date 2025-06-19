"""
Tests for exception classes and error handling.
"""

from athena_client.exceptions import (
    APIError,
    AthenaError,
    AuthenticationError,
    ClientError,
    NetworkError,
    RateLimitError,
    RetryFailedError,
    ServerError,
    TimeoutError,
    ValidationError,
)


class TestAthenaError:
    """Test base AthenaError class."""

    def test_athena_error_initialization(self):
        """Test AthenaError initialization."""
        error = AthenaError("Test error message")
        assert error.message == "Test error message"
        assert error.error_code is None  # Default value
        assert error.troubleshooting is None  # Default value

    def test_athena_error_string_representation(self):
        """Test AthenaError string representation."""
        error = AthenaError("Test error message")
        error_str = str(error)
        assert "Test error message" in error_str
        # No troubleshooting since it's None

    def test_athena_error_with_custom_values(self):
        """Test AthenaError with custom error_code and troubleshooting."""
        error = AthenaError(
            "Test error message",
            error_code="TEST_ERROR",
            troubleshooting="• Step 1\n• Step 2",
        )
        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.troubleshooting == "• Step 1\n• Step 2"

    def test_athena_error_string_with_troubleshooting(self):
        """Test AthenaError string representation with troubleshooting."""
        error = AthenaError("Test error message", troubleshooting="• Step 1\n• Step 2")
        error_str = str(error)
        assert "Test error message" in error_str
        assert "Step 1" in error_str
        assert "Step 2" in error_str

    def test_athena_error_default_values(self):
        """Test AthenaError default values."""
        error = AthenaError("Simple error")
        assert error.error_code is None  # Default value
        assert error.troubleshooting is None  # Default value


class TestNetworkError:
    """Test NetworkError class."""

    def test_network_error_initialization(self):
        """Test NetworkError initialization."""
        error = NetworkError("Connection failed")
        assert error.message == "Connection failed"
        assert error.error_code == "NETWORK_ERROR"
        assert "internet connection" in error.troubleshooting.lower()

    def test_network_error_with_url(self):
        """Test NetworkError with URL context."""
        error = NetworkError("Connection failed", url="https://api.example.com/test")
        assert "Connection failed" in str(error)

    def test_network_error_message(self):
        err = NetworkError("Connection failed")
        assert "Connection failed" in str(err)


class TestTimeoutError:
    """Test TimeoutError class."""

    def test_timeout_error_initialization(self):
        """Test TimeoutError initialization."""
        error = TimeoutError("Request timeout")
        assert error.message == "Request timeout"
        assert error.error_code == "NETWORK_ERROR"
        assert "timeout" in error.troubleshooting.lower()

    def test_timeout_error_with_timeout_value(self):
        """Test TimeoutError with timeout value."""
        error = TimeoutError("Request timeout")
        assert "Request timeout" in str(error)

    def test_timeout_error_message(self):
        err = TimeoutError("Request timed out")
        assert "Request timed out" in str(err)


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_initialization(self):
        """Test ValidationError initialization."""
        error = ValidationError("Invalid JSON response")
        assert error.message == "Invalid JSON response"
        assert error.error_code == "VALIDATION_ERROR"
        assert "api response format" in error.troubleshooting.lower()

    def test_validation_error_string_representation(self):
        """Test ValidationError string representation."""
        error = ValidationError("Invalid JSON response")
        error_str = str(error)
        assert "Invalid JSON response" in error_str

    def test_validation_error_message(self):
        err = ValidationError("Invalid data")
        assert "Invalid data" in str(err)


class TestAuthenticationError:
    """Test AuthenticationError class."""

    def test_authentication_error_initialization(self):
        """Test AuthenticationError initialization."""
        error = AuthenticationError("Unauthorized access", status_code=403)
        assert error.message == "Unauthorized access"
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.status_code == 403
        assert "authentication" in error.troubleshooting.lower()

    def test_authentication_error_string_representation(self):
        """Test AuthenticationError string representation."""
        error = AuthenticationError("Unauthorized access", status_code=403)
        error_str = str(error)
        assert "Unauthorized access" in error_str

    def test_authentication_error_message(self):
        err = AuthenticationError("Unauthorized", status_code=401)
        assert "Unauthorized" in str(err)


class TestRateLimitError:
    """Test RateLimitError class."""

    def test_rate_limit_error_initialization(self):
        """Test RateLimitError initialization."""
        error = RateLimitError("Rate limit exceeded", status_code=429)
        assert error.message == "Rate limit exceeded"
        assert error.error_code == "RATE_LIMIT_ERROR"
        assert error.status_code == 429
        assert "rate limit" in error.troubleshooting.lower()

    def test_rate_limit_error_string_representation(self):
        """Test RateLimitError string representation."""
        error = RateLimitError("Rate limit exceeded", status_code=429)
        error_str = str(error)
        assert "Rate limit exceeded" in error_str

    def test_rate_limit_error_message(self):
        err = RateLimitError("Rate limit exceeded", status_code=429)
        assert "Rate limit exceeded" in str(err)


class TestClientError:
    """Test ClientError class."""

    def test_client_error_initialization(self):
        """Test ClientError initialization."""
        error = ClientError("Bad request", status_code=400)
        assert error.message == "Bad request"
        assert error.error_code == "CLIENT_ERROR"
        assert error.status_code == 400
        assert "request parameters" in error.troubleshooting.lower()

    def test_client_error_string_representation(self):
        """Test ClientError string representation."""
        error = ClientError("Invalid parameters", status_code=422)
        error_str = str(error)
        assert "Invalid parameters" in error_str

    def test_client_error_message(self):
        err = ClientError("Bad request", status_code=400)
        assert "Bad request" in str(err)


class TestServerError:
    """Test ServerError class."""

    def test_server_error_initialization(self):
        """Test ServerError initialization."""
        error = ServerError("Service unavailable", status_code=503)
        assert error.message == "Service unavailable"
        assert error.error_code == "SERVER_ERROR"
        assert error.status_code == 503
        assert "server" in error.troubleshooting.lower()

    def test_server_error_string_representation(self):
        """Test ServerError string representation."""
        error = ServerError("Service unavailable", status_code=503)
        error_str = str(error)
        assert "Service unavailable" in error_str

    def test_server_error_message(self):
        err = ServerError("Internal error", status_code=500)
        assert "Internal error" in str(err)


class TestAPIError:
    """Test APIError class."""

    def test_api_error_initialization(self):
        """Test APIError initialization."""
        error = APIError("Search failed", api_error_code="INVALID_QUERY")
        assert error.message == "Search failed"
        assert error.error_code == "API_ERROR"
        assert error.api_error_code == "INVALID_QUERY"

    def test_api_error_string_representation(self):
        """Test APIError string representation."""
        error = APIError("Search failed", api_error_code="INVALID_QUERY")
        error_str = str(error)
        assert "Search failed" in error_str

    def test_api_error_message(self):
        err = APIError("Concept not found", api_error_code="NOT_FOUND")
        assert "Concept not found" in str(err)


class TestRetryFailedError:
    """Test RetryFailedError class."""

    def test_retry_failed_error_initialization(self):
        """Test RetryFailedError initialization."""
        last_error = NetworkError("Connection failed")
        error = RetryFailedError(
            "Retry failed after 3 attempts",
            max_attempts=3,
            last_error=last_error,
            retry_history=[last_error, last_error, last_error],
        )

        assert error.message == "Retry failed after 3 attempts"
        assert error.error_code == "RETRY_FAILED"
        assert error.max_attempts == 3
        assert error.last_error == last_error

    def test_retry_failed_error_message(self):
        err = RetryFailedError(
            "Retry failed after 3 attempts",
            max_attempts=3,
            last_error="Timeout",
            retry_history=["Timeout", "Timeout", "Timeout"],
        )
        assert "Retry failed after 3 attempts" in str(err)
        assert "3" in str(err)
        assert "Timeout" in str(err)


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from AthenaError."""
        exceptions = [
            NetworkError("test"),
            TimeoutError("test"),
            ValidationError("test"),
            AuthenticationError("test", status_code=401),
            RateLimitError("test", status_code=429),
            ClientError("test", status_code=400),
            ServerError("test", status_code=500),
            APIError("test"),
            RetryFailedError("test", 1, NetworkError("test"), []),
        ]

        for exc in exceptions:
            assert hasattr(exc, "message")
            assert hasattr(exc, "error_code")
            assert hasattr(exc, "troubleshooting")

    def test_exception_types(self):
        """Test that exceptions are of correct types."""
        assert isinstance(NetworkError("test"), NetworkError)
        assert isinstance(TimeoutError("test"), TimeoutError)
        assert isinstance(ValidationError("test"), ValidationError)
        assert isinstance(
            AuthenticationError("test", status_code=401), AuthenticationError
        )
        assert isinstance(RateLimitError("test", status_code=429), RateLimitError)
        assert isinstance(ClientError("test", status_code=400), ClientError)
        assert isinstance(ServerError("test", status_code=500), ServerError)
        assert isinstance(APIError("test"), APIError)
        assert isinstance(
            RetryFailedError("test", 1, NetworkError("test"), []), RetryFailedError
        )


class TestExceptionContext:
    """Test exception context and troubleshooting."""

    def test_network_error_context(self):
        """Test NetworkError provides network-specific troubleshooting."""
        error = NetworkError("Connection failed")
        assert "internet connection" in error.troubleshooting.lower()
        assert "network" in error.troubleshooting.lower()

    def test_authentication_error_context(self):
        """Test AuthenticationError provides auth-specific troubleshooting."""
        error = AuthenticationError("Invalid token")
        assert "token" in error.troubleshooting.lower()
        assert "authentication" in error.troubleshooting.lower()

    def test_rate_limit_error_context(self):
        """Test RateLimitError provides rate limit-specific troubleshooting."""
        error = RateLimitError("Rate limit exceeded", status_code=429)
        assert "rate limit" in error.troubleshooting.lower()
        assert "wait" in error.troubleshooting.lower()

    def test_validation_error_context(self):
        """Test ValidationError provides validation-specific troubleshooting."""
        error = ValidationError("Invalid data")
        assert "api response format" in error.troubleshooting.lower()

    def test_retry_failed_error_context(self):
        """Test RetryFailedError provides retry-specific troubleshooting."""
        error = RetryFailedError("Failed", 3, NetworkError("test"), [])
        assert "retry attempts have been exhausted" in error.troubleshooting
        assert "max_retries" in error.troubleshooting.lower()
