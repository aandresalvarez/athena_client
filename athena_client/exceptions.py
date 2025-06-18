"""
Exception classes for the Athena client.

This module defines a hierarchy of exceptions that can be raised by the Athena client.
"""
from typing import Optional


class AthenaError(Exception):
    """Base class for all Athena client exceptions."""
    
    def __init__(self, message: str) -> None:
        """
        Initialize the exception.
        
        Args:
            message: Error message
        """
        super().__init__(message)
        self.message = message


class NetworkError(AthenaError):
    """
    Raised for network-related errors (DNS, TLS, socket, or timeout).
    """
    pass


class ServerError(AthenaError):
    """
    Raised when the server returns a 5xx status code.
    """
    
    def __init__(
        self, message: str, status_code: int, response: Optional[str] = None
    ) -> None:
        """
        Initialize the exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response: Raw response body
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ClientError(AthenaError):
    """
    Raised when the server returns a 4xx status code.
    """
    
    def __init__(
        self, message: str, status_code: int, response: Optional[str] = None
    ) -> None:
        """
        Initialize the exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response: Raw response body
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(AthenaError):
    """
    Raised when response validation fails.
    """
    pass
