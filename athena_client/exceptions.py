"""
Exception classes for the Athena client.

This module defines a hierarchy of exceptions that can be raised by the Athena client.
"""

from typing import List, Optional


class AthenaError(Exception):
    """Base class for all Athena client exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        troubleshooting: Optional[str] = None,
    ) -> None:
        """
        Initialize the exception.

        Args:
            message: Error message
            error_code: Optional error code for programmatic handling
            troubleshooting: Optional troubleshooting suggestions
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.troubleshooting = troubleshooting

    def __str__(self) -> str:
        """Return a user-friendly error message."""
        msg = self.message
        if self.troubleshooting:
            msg += f"\n\n💡 Troubleshooting: {self.troubleshooting}"
        return msg


class NetworkError(AthenaError):
    """
    Raised for network-related errors (DNS, TLS, socket, or timeout).
    """

    def __init__(self, message: str, url: Optional[str] = None) -> None:
        """
        Initialize the network error.

        Args:
            message: Error message
            url: URL that failed to connect
        """
        troubleshooting = (
            "• Check your internet connection\n"
            "• Verify the API endpoint URL is correct\n"
            "• Try again in a few moments\n"
            "• Contact your network administrator if the problem persists"
        )
        super().__init__(
            message, error_code="NETWORK_ERROR", troubleshooting=troubleshooting
        )
        self.url = url


class TimeoutError(NetworkError):
    """
    Raised when a request times out.
    """

    def __init__(
        self, message: str, url: Optional[str] = None, timeout: Optional[float] = None
    ) -> None:
        """
        Initialize the timeout error.

        Args:
            message: Error message
            url: URL that timed out
            timeout: Timeout value that was exceeded
        """
        troubleshooting = (
            "• The server is taking too long to respond\n"
            "• Try increasing the timeout value\n"
            "• Check if the API server is experiencing high load\n"
            "• Try again in a few moments"
        )
        super().__init__(message, url)
        self.timeout = timeout
        self.troubleshooting = troubleshooting


class ServerError(AthenaError):
    """
    Raised when the server returns a 5xx status code.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize the server error.

        Args:
            message: Error message
            status_code: HTTP status code
            response: Raw response body
            url: URL that caused the error
        """
        troubleshooting = (
            "• The API server is experiencing issues\n"
            "• Try again in a few moments\n"
            "• Check the API status page for known issues\n"
            "• Contact the API administrators if the problem persists"
        )
        super().__init__(
            message, error_code="SERVER_ERROR", troubleshooting=troubleshooting
        )
        self.status_code = status_code
        self.response = response
        self.url = url


class ClientError(AthenaError):
    """
    Raised when the server returns a 4xx status code.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize the client error.

        Args:
            message: Error message
            status_code: HTTP status code
            response: Raw response body
            url: URL that caused the error
        """
        # Customize troubleshooting based on status code
        if status_code == 400:
            troubleshooting = (
                "• Check your request parameters\n"
                "• Verify the data format is correct\n"
                "• Review the API documentation for the correct format"
            )
        elif status_code == 401:
            troubleshooting = (
                "• Check your authentication credentials\n"
                "• Verify your API token is valid and not expired\n"
                "• Ensure you have the necessary permissions"
            )
        elif status_code == 403:
            troubleshooting = (
                "• You don't have permission to access this resource\n"
                "• Check your API token permissions\n"
                "• Contact the API administrators for access"
            )
        elif status_code == 404:
            troubleshooting = (
                "• The requested resource was not found\n"
                "• Check the URL path is correct\n"
                "• Verify the resource ID exists\n"
                "• Review the API documentation for available endpoints"
            )
        elif status_code == 429:
            troubleshooting = (
                "• You've exceeded the rate limit\n"
                "• Wait before making more requests\n"
                "• Consider implementing request throttling\n"
                "• Check the API documentation for rate limits"
            )
        else:
            troubleshooting = (
                "• Check your request parameters\n"
                "• Review the API documentation\n"
                "• Verify your authentication credentials"
            )

        super().__init__(
            message, error_code="CLIENT_ERROR", troubleshooting=troubleshooting
        )
        self.status_code = status_code
        self.response = response
        self.url = url


class ValidationError(AthenaError):
    """
    Raised when response validation fails.
    """

    def __init__(self, message: str, validation_details: Optional[str] = None) -> None:
        """
        Initialize the validation error.

        Args:
            message: Error message
            validation_details: Detailed validation error information
        """
        troubleshooting = (
            "• The API response format has changed\n"
            "• This might be a temporary API issue\n"
            "• Try again in a few moments\n"
            "• Contact the API administrators if the problem persists"
        )
        super().__init__(
            message, error_code="VALIDATION_ERROR", troubleshooting=troubleshooting
        )
        self.validation_details = validation_details


class AuthenticationError(ClientError):
    """
    Raised for authentication-related errors.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 401,
        response: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize the authentication error.

        Args:
            message: Error message
            status_code: HTTP status code (default 401)
            response: Raw response body
            url: URL that caused the error
        """
        troubleshooting = (
            "• Check your API token is valid and not expired\n"
            "• Verify your authentication credentials\n"
            "• Ensure you have the necessary permissions\n"
            "• Contact the API administrators for access"
        )
        super().__init__(message, status_code, response, url)
        self.error_code = "AUTHENTICATION_ERROR"
        self.troubleshooting = troubleshooting


class RateLimitError(ClientError):
    """
    Raised when rate limits are exceeded.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        response: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """
        Initialize the rate limit error.

        Args:
            message: Error message
            status_code: HTTP status code (default 429)
            response: Raw response body
            url: URL that caused the error
        """
        troubleshooting = (
            "• You've exceeded the API rate limit\n"
            "• Wait before making more requests\n"
            "• Consider implementing request throttling\n"
            "• Check the API documentation for rate limits"
        )
        super().__init__(message, status_code, response, url)
        self.error_code = "RATE_LIMIT_ERROR"
        self.troubleshooting = troubleshooting


class APIError(AthenaError):
    """
    Raised when the API returns an error response.
    """

    def __init__(
        self,
        message: str,
        api_error_code: Optional[str] = None,
        api_message: Optional[str] = None,
    ) -> None:
        """
        Initialize the API error.

        Args:
            message: Error message
            api_error_code: Error code from the API
            api_message: Error message from the API
        """
        troubleshooting = (
            "• The API returned an error response\n"
            "• Check the API error details above\n"
            "• Verify your request parameters\n"
            "• Try again with different parameters if applicable"
        )
        super().__init__(
            message, error_code="API_ERROR", troubleshooting=troubleshooting
        )
        self.api_error_code = api_error_code
        self.api_message = api_message


class RetryFailedError(AthenaError):
    """
    Raised when all retry attempts have been exhausted.
    """

    def __init__(
        self,
        message: str,
        max_attempts: int,
        last_error: Exception,
        retry_history: List[Exception],
        error_code: Optional[str] = None,
    ) -> None:
        """
        Initialize the retry failed error.

        Args:
            message: Error message
            max_attempts: Maximum number of retry attempts
            last_error: The last error that caused the final failure
            retry_history: List of errors from each retry attempt
            error_code: Optional error code
        """
        troubleshooting = (
            "• All retry attempts have been exhausted\n"
            "• Check your internet connection\n"
            "• Verify the API server is accessible\n"
            "• Try again in a few moments\n"
            "• Consider increasing max_retries if this is a temporary issue"
        )
        super().__init__(
            message,
            error_code=error_code or "RETRY_FAILED",
            troubleshooting=troubleshooting,
        )
        self.max_attempts = max_attempts
        self.last_error = last_error
        self.retry_history = retry_history

    def __str__(self) -> str:
        """Return a detailed error message with retry information."""
        msg = self.message
        msg += "\n\n📊 Retry Information:"
        msg += f"\n• Maximum attempts: {self.max_attempts}"
        msg += f"\n• Attempts made: {len(self.retry_history) + 1}"
        msg += f"\n• Last error: {type(self.last_error).__name__}: {self.last_error}"

        if self.retry_history:
            msg += "\n\n🔄 Retry History:"
            for i, error in enumerate(self.retry_history, 1):
                msg += f"\n• Attempt {i}: {type(error).__name__}: {error}"

        if self.troubleshooting:
            msg += f"\n\n💡 Troubleshooting: {self.troubleshooting}"

        return msg
