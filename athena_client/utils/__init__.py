"""
Utility functions for the Athena client.

This module provides various utility functions for the Athena client,
including progress tracking, query size estimation, and timeout management.
"""

import logging
from typing import Optional

from .progress import (
    ProgressTracker,
    estimate_query_size,
    format_large_query_warning,
    get_operation_timeout,
    progress_context,
)

logger = logging.getLogger(__name__)


def configure_logging(level: Optional[int] = None) -> None:
    """
    Configure logging for the Athena client.

    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    log_level = level or logging.INFO

    logger = logging.getLogger("athena_client")
    logger.setLevel(log_level)

    # Create console handler if no handlers exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)


__all__ = [
    "configure_logging",
    "ProgressTracker",
    "progress_context",
    "estimate_query_size",
    "get_operation_timeout",
    "format_large_query_warning",
]
