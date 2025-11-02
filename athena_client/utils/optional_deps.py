"""
Utilities for handling optional dependencies gracefully.

This module provides standardized error handling for optional dependencies,
ensuring consistent user-facing error messages across the package.
"""

from typing import NoReturn, Optional


def require_optional_package(
    package_name: str,
    feature: str,
    extra: str,
    import_error: Optional[ImportError] = None,
) -> NoReturn:
    """
    Raise a standardized error for missing optional dependencies.

    Args:
        package_name: Name of the missing package (e.g., "pandas")
        feature: Feature that requires the package (e.g., "DataFrame support")
        extra: pip extra to install (e.g., "pandas")
        import_error: Original ImportError that triggered this (optional)

    Raises:
        ImportError: With helpful message about installing the extra

    Example:
        >>> try:
        ...     import pandas
        ... except ImportError as e:
        ...     require_optional_package("pandas", "DataFrame support", "pandas", e)
    """
    raise ImportError(
        f"{package_name} is required for {feature}. "
        f"Install with: pip install 'athena-client[{extra}]'"
    ) from import_error


def check_optional_package(package_name: str) -> bool:
    """
    Check if an optional package is available without importing it.

    Args:
        package_name: Name of the package to check

    Returns:
        True if package is available, False otherwise

    Example:
        >>> if check_optional_package("pandas"):
        ...     import pandas as pd
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False
