"""Tests for the utils module."""

import logging
from unittest.mock import Mock, patch

from athena_client.utils import configure_logging


class TestUtils:
    """Test cases for the utils module."""

    def test_configure_logging_default_level(self):
        """Test logging configuration with default level."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO

            configure_logging()

            mock_logging.getLogger.assert_called_with("athena_client")
            mock_logger.setLevel.assert_called_with(logging.INFO)

    def test_configure_logging_custom_level(self):
        """Test logging configuration with custom level."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.DEBUG = logging.DEBUG

            configure_logging(logging.DEBUG)

            mock_logger.setLevel.assert_called_with(logging.DEBUG)

    def test_configure_logging_with_existing_handlers(self):
        """Test logging configuration when handlers already exist."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logger.handlers = [Mock()]  # Existing handler
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO
            mock_logging.StreamHandler = Mock()
            mock_logging.Formatter = Mock()

            configure_logging()

            # Should not add new handler when handlers already exist
            mock_logging.StreamHandler.assert_not_called()

    def test_configure_logging_without_handlers(self):
        """Test logging configuration when no handlers exist."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logger.handlers = []  # No existing handlers
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO

            mock_handler = Mock()
            mock_logging.StreamHandler.return_value = mock_handler

            mock_formatter = Mock()
            mock_logging.Formatter.return_value = mock_formatter

            configure_logging()

            # Should create new handler and formatter
            mock_logging.StreamHandler.assert_called_once()
            mock_logging.Formatter.assert_called_once()
            mock_handler.setLevel.assert_called_with(logging.INFO)
            mock_handler.setFormatter.assert_called_with(mock_formatter)
            mock_logger.addHandler.assert_called_with(mock_handler)

    def test_configure_logging_none_level(self):
        """Test logging configuration with None level."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO

            configure_logging(None)

            # Should use default INFO level
            mock_logger.setLevel.assert_called_with(logging.INFO)

    def test_configure_logging_formatter_format(self):
        """Test that the formatter is created with the correct format."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO

            mock_handler = Mock()
            mock_logging.StreamHandler.return_value = mock_handler

            mock_formatter = Mock()
            mock_logging.Formatter.return_value = mock_formatter

            configure_logging()

            # Should create formatter with the correct format string
            expected_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            mock_logging.Formatter.assert_called_with(expected_format)

    def test_configure_logging_handler_level(self):
        """Test that the handler level is set correctly."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO

            mock_handler = Mock()
            mock_logging.StreamHandler.return_value = mock_handler

            mock_formatter = Mock()
            mock_logging.Formatter.return_value = mock_formatter

            configure_logging(logging.DEBUG)

            # Handler level should match the configured level
            mock_handler.setLevel.assert_called_with(logging.DEBUG)

    def test_configure_logging_logger_name(self):
        """Test that the correct logger name is used."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO

            configure_logging()

            # Should get logger with the correct name
            mock_logging.getLogger.assert_called_with("athena_client")

    def test_configure_logging_multiple_calls(self):
        """Test that multiple calls to configure_logging work correctly."""
        with patch("athena_client.utils.logging") as mock_logging:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_logging.getLogger.return_value = mock_logger
            mock_logging.INFO = logging.INFO
            mock_logging.DEBUG = logging.DEBUG

            mock_handler = Mock()
            mock_logging.StreamHandler.return_value = mock_handler

            mock_formatter = Mock()
            mock_logging.Formatter.return_value = mock_formatter

            # First call
            configure_logging(logging.INFO)

            # Second call with different level
            configure_logging(logging.DEBUG)

            # Should set level to DEBUG on second call
            assert mock_logger.setLevel.call_count == 2
            mock_logger.setLevel.assert_called_with(logging.DEBUG)

    def test_configure_logging_integration(self):
        """Test logging configuration integration with real logging."""
        # Test with real logging module
        original_handlers = logging.getLogger("athena_client").handlers[:]

        try:
            # Configure logging
            configure_logging(logging.DEBUG)

            # Get the logger
            logger = logging.getLogger("athena_client")

            # Check that level is set correctly
            assert logger.level == logging.DEBUG

            # Check that handlers were added
            assert len(logger.handlers) > 0

            # Check that handler level is set correctly
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    assert handler.level == logging.DEBUG
                    assert handler.formatter is not None

        finally:
            # Clean up - remove handlers we added
            logger = logging.getLogger("athena_client")
            for handler in logger.handlers[:]:
                if handler not in original_handlers:
                    logger.removeHandler(handler)
