"""
Progress tracking utilities for large queries.

This module provides progress indicators and user-friendly feedback
for long-running operations like large searches and graph queries.
"""

import threading
import time
from contextlib import contextmanager
from typing import Generator, Optional


class ProgressTracker:
    """Track progress of long-running operations with user-friendly feedback."""

    def __init__(
        self,
        total: int,
        description: str = "Processing",
        show_progress: bool = True,
        update_interval: float = 2.0,
    ) -> None:
        """
        Initialize the progress tracker.

        Args:
            total: Total number of items to process
            description: Description of the operation
            show_progress: Whether to show progress updates
            update_interval: Seconds between progress updates
        """
        self.total = total
        self.description = description
        self.show_progress = show_progress
        self.update_interval = update_interval
        self.current = 0
        self.start_time: Optional[float] = None
        self.last_update_time: float = 0.0
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start tracking progress."""
        self.start_time = time.time()
        if self.show_progress:
            self._print_progress()

    def update(self, increment: int = 1) -> None:
        """
        Update progress by the given increment.

        Args:
            increment: Number of items completed
        """
        with self._lock:
            self.current += increment
            current_time = time.time()

            # Only update display if enough time has passed
            if (
                self.show_progress
                and current_time - self.last_update_time >= self.update_interval
            ):
                self._print_progress()
                self.last_update_time = current_time

    def complete(self) -> None:
        """Mark the operation as complete."""
        self.current = self.total
        if self.show_progress:
            self._print_progress()
            print(f"✅ {self.description} completed!")

    def _print_progress(self) -> None:
        """Print the current progress."""
        if self.total == 0:
            return

        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time if self.start_time else 0

        # Calculate ETA
        eta = None
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            remaining = self.total - self.current
            eta = remaining / rate if rate > 0 else None

        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        # Format time
        elapsed_str = self._format_time(elapsed)
        eta_str = f" (ETA: {self._format_time(eta)})" if eta else ""

        print(
            f"\r{self.description}: [{bar}] {percentage:.1f}% "
            f"({self.current}/{self.total}) {elapsed_str}{eta_str}",
            end="",
            flush=True,
        )

    def _format_time(self, seconds: Optional[float]) -> str:
        """Format time in a human-readable way."""
        if seconds is None:
            return "unknown"

        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


@contextmanager
def progress_context(
    total: int,
    description: str = "Processing",
    show_progress: bool = True,
    update_interval: float = 2.0,
) -> Generator[ProgressTracker, None, None]:
    """
    Context manager for progress tracking.

    Args:
        total: Total number of items to process
        description: Description of the operation
        show_progress: Whether to show progress updates
        update_interval: Seconds between progress updates

    Yields:
        ProgressTracker instance
    """
    tracker = ProgressTracker(total, description, show_progress, update_interval)
    try:
        tracker.start()
        yield tracker
    finally:
        tracker.complete()


def estimate_query_size(query: str) -> int:
    """
    Estimate the size of a query based on its characteristics.

    Args:
        query: The search query string

    Returns:
        Estimated number of results
    """
    # Simple heuristics for query size estimation
    query_lower = query.lower()

    # Very broad queries
    if len(query) <= 2:
        return 10000  # Very broad, likely many results

    # Common medical terms that are likely to have many results
    broad_terms = [
        "pain",
        "fever",
        "headache",
        "cough",
        "diabetes",
        "hypertension",
        "cancer",
        "heart",
        "lung",
        "liver",
        "kidney",
        "blood",
        "infection",
    ]

    if any(term in query_lower for term in broad_terms):
        return 5000

    # Specific terms with modifiers
    if any(word in query_lower for word in ["acute", "chronic", "severe", "mild"]):
        return 2000

    # Very specific terms (likely fewer results)
    if len(query) > 10 and any(char.isdigit() for char in query):
        return 500

    # Default estimate
    return 1000


def get_operation_timeout(operation_type: str, query_size: Optional[int] = None) -> int:
    """
    Get appropriate timeout for different operation types.

    Args:
        operation_type: Type of operation ('search', 'graph', 'relationships')
        query_size: Estimated size of the query

    Returns:
        Timeout in seconds
    """
    from athena_client.settings import get_settings

    settings = get_settings()

    # Base timeouts
    base_timeouts = {
        "search": settings.ATHENA_SEARCH_TIMEOUT_SECONDS,
        "graph": settings.ATHENA_GRAPH_TIMEOUT_SECONDS,
        "relationships": settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS,
        "details": settings.ATHENA_TIMEOUT_SECONDS,
    }

    base_timeout = base_timeouts.get(operation_type, settings.ATHENA_TIMEOUT_SECONDS)

    # Adjust based on query size
    if query_size:
        if query_size > 10000:
            return int(base_timeout * 2.5)  # Very large queries
        elif query_size > 5000:
            return int(base_timeout * 2.0)  # Large queries
        elif query_size > 1000:
            return int(base_timeout * 1.5)  # Medium queries

    return base_timeout


def format_large_query_warning(query: str, estimated_size: int) -> str:
    """
    Generate a user-friendly warning for large queries.

    Args:
        query: The search query
        estimated_size: Estimated number of results

    Returns:
        Warning message
    """
    if estimated_size < 1000:
        return ""

    warning = f"⚠️  Large query detected: '{query}' "

    if estimated_size > 10000:
        warning += f"(estimated {estimated_size:,}+ results)\n"
        warning += "💡 Suggestions:\n"
        warning += "   • Add more specific terms to narrow results\n"
        warning += "   • Use domain or vocabulary filters\n"
        warning += "   • Consider using smaller page sizes\n"
        warning += "   • This query may take several minutes to complete"
    elif estimated_size > 5000:
        warning += f"(estimated {estimated_size:,}+ results)\n"
        warning += "💡 Consider adding filters to reduce results"
    else:
        warning += f"(estimated {estimated_size:,}+ results)"

    return warning
