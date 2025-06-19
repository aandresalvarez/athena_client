"""
Utility functions for the Athena client.
"""

import logging
from typing import Optional

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


# Export progress utilities
from .progress import (
    ProgressTracker,
    progress_context,
    estimate_query_size,
    get_operation_timeout,
    format_large_query_warning,
)

__all__ = [
    "configure_logging",
    "ProgressTracker",
    "progress_context", 
    "estimate_query_size",
    "get_operation_timeout",
    "format_large_query_warning",
]
