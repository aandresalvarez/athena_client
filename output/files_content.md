# 📂 Project File Contents

- 📁 **athena_client**
  - [`CONTRIBUTING.md`](#athena_client-contributingmd)
  - [`README.md`](#athena_client-readmemd)
  - [`extract.py`](#athena_client-extractpy)
  - [`pyproject.toml`](#athena_client-pyprojecttoml)
  - [`setup.py`](#athena_client-setuppy)
    - 📁 **workflows**
      - [`ci.yml`](#athena_client-github-workflows-ciyml)
  - 📁 **.pytest_cache**
    - [`README.md`](#athena_client-pytest_cache-readmemd)
  - 📁 **athena_client**
    - [`__init__.py`](#athena_client-athena_client-__init__py)
    - [`async_client.py`](#athena_client-athena_client-async_clientpy)
    - [`auth.py`](#athena_client-athena_client-authpy)
    - [`cli.py`](#athena_client-athena_client-clipy)
    - [`client.py`](#athena_client-athena_client-clientpy)
    - [`exceptions.py`](#athena_client-athena_client-exceptionspy)
    - [`http.py`](#athena_client-athena_client-httppy)
    - [`query.py`](#athena_client-athena_client-querypy)
    - [`search_result.py`](#athena_client-athena_client-search_resultpy)
    - [`settings.py`](#athena_client-athena_client-settingspy)
  - 📁 **athena_client.egg-info**
    - [`SOURCES.txt`](#athena_client-athena_clientegg-info-sourcestxt)
    - [`dependency_links.txt`](#athena_client-athena_clientegg-info-dependency_linkstxt)
    - [`entry_points.txt`](#athena_client-athena_clientegg-info-entry_pointstxt)
    - [`requires.txt`](#athena_client-athena_clientegg-info-requirestxt)
    - [`top_level.txt`](#athena_client-athena_clientegg-info-top_leveltxt)
    - 📁 **models**
      - [`__init__.py`](#athena_client-athena_client-models-__init__py)
    - 📁 **utils**
      - [`__init__.py`](#athena_client-athena_client-utils-__init__py)
      - 📁 **athena_client**
        - [`__init__.py`](#athena_client-build-lib-athena_client-__init__py)
        - [`async_client.py`](#athena_client-build-lib-athena_client-async_clientpy)
        - [`auth.py`](#athena_client-build-lib-athena_client-authpy)
        - [`cli.py`](#athena_client-build-lib-athena_client-clipy)
        - [`client.py`](#athena_client-build-lib-athena_client-clientpy)
        - [`exceptions.py`](#athena_client-build-lib-athena_client-exceptionspy)
        - [`http.py`](#athena_client-build-lib-athena_client-httppy)
        - [`query.py`](#athena_client-build-lib-athena_client-querypy)
        - [`search_result.py`](#athena_client-build-lib-athena_client-search_resultpy)
        - [`settings.py`](#athena_client-build-lib-athena_client-settingspy)
        - 📁 **models**
          - [`__init__.py`](#athena_client-build-lib-athena_client-models-__init__py)
        - 📁 **utils**
          - [`__init__.py`](#athena_client-build-lib-athena_client-utils-__init__py)
  - 📁 **examples**
    - [`simple_demo.py`](#athena_client-examples-simple_demopy)
  - 📁 **tests**
    - [`__init__.py`](#athena_client-tests-__init__py)
    - [`conftest.py`](#athena_client-tests-conftestpy)
    - [`test_query.py`](#athena_client-tests-test_querypy)
    - [`test_search_result.py`](#athena_client-tests-test_search_resultpy)
    - 📁 **benchmarks**
      - [`test_orjson.py`](#athena_client-tests-benchmarks-test_orjsonpy)
    - 📁 **property**
      - [`test_query_builder.py`](#athena_client-tests-property-test_query_builderpy)

---

# Target Folder: athena_client

## Folder: athena_client

> ℹ️ *Note: Contains a virtual environment folder (e.g., `venv`, `.venv`). Contents are excluded.*

### File: `athena_client/CONTRIBUTING.md`
<a name="athena_client-contributingmd"></a>
```markdown
# Contributing to Athena Client

Thank you for considering a contribution!

### Quick Start

```bash
pip install hatch
make install
make quality   # format + lint + mypy + bandit
make test      # unit, async & property tests
```

### Security Checks

We run **Bandit** on every pull request. Execute locally with:

```bash
make bandit
```

The CI build fails on any high-severity finding.

```

### File: `athena_client/README.md`
<a name="athena_client-readmemd"></a>
```markdown
# athena-client
[![SBOM](https://img.shields.io/badge/SBOM-available-blue)](sbom.json)

A production-ready Python SDK for the OHDSI Athena Concepts API.

## Installation

```bash
pip install athena-client
```

With optional dependencies:
```bash
pip install athena-client[cli]      # Command-line interface
pip install athena-client[async]    # Async client
pip install athena-client[pandas]   # DataFrame output support
pip install athena-client[yaml]     # YAML output format
pip install athena-client[crypto]   # HMAC authentication
pip install athena-client[all]      # All optional dependencies
```

## Quick Start

```python
from athena_client import Athena

# Create a client with default settings (public Athena server)
athena = Athena()

# Search for concepts
results = athena.search("aspirin")

# Various output formats
concepts = results.all()         # List of Pydantic models
top_three = results.top(3)       # First three results
as_dict = results.to_list()      # List of dictionaries
as_json = results.to_json()      # JSON string
as_df = results.to_df()          # pandas DataFrame

# Get details for a specific concept
details = athena.details(concept_id=1127433)

# Get relationships
rels = athena.relationships(concept_id=1127433)

# Get graph
graph = athena.graph(concept_id=1127433, depth=5)

# Get comprehensive summary
summary = athena.summary(concept_id=1127433)
```

## CLI Usage

```bash
# Install CLI dependencies
pip install "athena-client[cli]"

# Search for concepts
athena search "aspirin"

# Get details for a specific concept
athena details 1127433

# Get a summary with various output formats
athena summary 1127433 --output yaml
```

## Configuration

The client can be configured through:
1. Constructor arguments
2. Environment variables
3. A `.env` file
4. Default values

```python
# Explicit configuration
athena = Athena(
    base_url="https://custom.athena.server/api/v1",
    token="your-bearer-token",
    timeout=15,
    max_retries=5
)
```

Or use environment variables:
```
ATHENA_BASE_URL=https://custom.athena.server/api/v1
ATHENA_TOKEN=your-bearer-token
ATHENA_TIMEOUT_SECONDS=15
ATHENA_MAX_RETRIES=5
```

## Advanced Query DSL

For complex queries, use the Query DSL:

```python
from athena_client.query import Q

# Build complex queries
q = (Q.term("diabetes") & Q.term("type 2")) | Q.exact('"diabetic nephropathy"')

# Use with search
results = athena.search(q)
```

### Property-Based Tests

We use **Hypothesis** for edge-case discovery. New core utilities or parsers **must** include at least one Hypothesis scenario.

## Modern Installation & Packaging

This project uses the modern Python packaging standard with `pyproject.toml` for build and dependency management. You do not need to use `setup.py` for installation or development. Instead, use the following commands:

### Install with pip (recommended)

```bash
pip install .
```

Or, for development (editable install with dev dependencies):

> **Note:** For editable installs with extras, make sure you have recent versions of pip and setuptools:
> ```bash
> pip install --upgrade pip setuptools
> ```
```bash
pip install -e '.[dev]'
```

### Why `pyproject.toml`?
- All build, dependency, and metadata configuration is in `pyproject.toml`.
- Compatible with modern Python tooling (pip, build, poetry, etc).
- `setup.py` is only needed for legacy or advanced customizations.

For more details, see [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## Documentation

For complete documentation, visit: [https://athena-client.readthedocs.io](https://athena-client.readthedocs.io)

## License

MIT

```

### File: `athena_client/pyproject.toml`
<a name="athena_client-pyprojecttoml"></a>
```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "athena-client"
version = "1.0.0"
description = "Production-ready Python SDK for the OHDSI Athena Concepts API"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Athena-Client Core Engineering Team"}
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Healthcare Industry",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
]
dependencies = [
    "requests>=2.25.0",
    "urllib3>=1.26.0",
    "backoff>=1.10.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "orjson>=3.9.0",
]

[project.optional-dependencies]
async = ["httpx>=0.18.0"]
pandas = ["pandas>=1.3.0"]
cli = ["click>=8.0.0", "rich>=10.0.0"]
yaml = ["pyyaml>=6.0"]
crypto = ["cryptography>=36.0.0"]
all = [
    "httpx>=0.18.0",
    "pandas>=1.3.0",
    "click>=8.0.0",
    "rich>=10.0.0",
    "pyyaml>=6.0",
    "cryptography>=36.0.0",
]
dev = [
  "ruff>=0.4.0",
  "mypy>=1.10",
  "pip-audit>=2.6",
  "pytest>=8.2",
  "pytest-cov>=5.0",
  "pytest-asyncio[mode-auto]>=0.23",
  "hypothesis>=6.103",
  "vcrpy>=6.0",
  "rich>=13.7",
  "build>=1.2",
  "twine>=5.1",
  "pytest-benchmark>=4.0",
  "bandit>=1.7.5",
  "cyclonedx-python-lib>=5.2.0",
  "types-requests",
  "types-PyYAML",
  "pandas-stubs"
]


[tool.hatch.envs.default]
features = ["dev", "all"]

[project.scripts]
athena = "athena_client.cli:main"

[project.urls]
Homepage = "https://github.com/username/athena-client"
Documentation = "https://athena-client.readthedocs.io"
Issues = "https://github.com/username/athena-client/issues"

[tool.black]
line-length = 88
target-version = ["py39"]


[tool.ruff]
target-version = "py39"
line-length = 88
lint.select = ["E", "F", "B", "I"]

[tool.mypy]
python_version = "3.9"
warn_redundant_casts = true
warn_unused_ignores = true
disallow_any_generics = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
strict_optional = true

[tool.hatch.envs.default.scripts]
lint = "ruff check athena_client tests"
format = "ruff format athena_client tests"
type-check = "mypy athena_client"
test = "pytest {args}"
cov = "pytest --cov=athena_client --cov-report=term-missing {args}"
bandit = "bandit -c pyproject.toml -r athena_client -s B101,B404,B603"
cyclonedx = "cyclonedx-py --format json --output sbom.json"

quality = [
  "format",
  "lint",
  "type-check",
  "bandit",
]


```

### File: `athena_client/setup.py`
<a name="athena_client-setuppy"></a>
```python
"""
Setup script for the athena-client package.
"""
from setuptools import setup

if __name__ == "__main__":
    setup()

```

## Folder: .pytest_cache

### File: `athena_client/.pytest_cache/README.md`
<a name="athena_client-pytest_cache-readmemd"></a>
```markdown
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

## Folder: .pytest_cache/v

## Folder: .pytest_cache/v/cache

## Folder: athena_client

### File: `athena_client/athena_client/__init__.py`
<a name="athena_client-athena_client-__init__py"></a>
```python
"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""

from typing import Any, Dict, Optional

from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship

__version__ = "1.0.0"


class Athena:
    """
    Main facade for the Athena API client.

    This class provides a simplified interface to the Athena API with six
    intuitive verbs that cover 95% of day-to-day use cases.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the Athena facade with optional configuration.

        Args:
            base_url: The base URL for the Athena API.
            token: Bearer token for authentication.
            client_id: Client ID for HMAC authentication.
            private_key: Private key for HMAC signing.
            timeout: HTTP timeout in seconds.
            max_retries: Maximum number of retry attempts.
            backoff_factor: Exponential backoff factor for retries.
        """
        # Import here to avoid circular imports
        from .client import AthenaClient  # pylint: disable=import-outside-toplevel

        self._client = AthenaClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def search(
        self,
        query: Any,  # Can be str or Q object
        *,
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> "SearchResult":
        """
        Search for concepts in the Athena vocabulary.

        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status

        Returns:
            SearchResult object containing the search results
        """
        from .search_result import SearchResult

        # Handle Q object if provided
        query_str = query
        if hasattr(query, "to_boosts") and callable(query.to_boosts):
            boosts = query.to_boosts()
            query_str = ""

        data = self._client.search_concepts(
            query=query_str,
            exact=exact,
            fuzzy=fuzzy,
            wildcard=wildcard,
            boosts=boosts,
            debug=debug,
            page_size=page_size,
            page=page,
            domain=domain,
            vocabulary=vocabulary,
            standard_concept=standard_concept,
        )

        return SearchResult(data)

    def details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.

        Args:
            concept_id: The concept ID to get details for

        Returns:
            ConceptDetails object
        """
        return self._client.get_concept_details(concept_id)

    def relationships(
        self,
        concept_id: int,
        *,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.

        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts

        Returns:
            ConceptRelationship object
        """
        return self._client.get_concept_relationships(
            concept_id=concept_id,
            relationship_id=relationship_id,
            only_standard=only_standard,
        )

    def graph(
        self,
        concept_id: int,
        *,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.

        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph

        Returns:
            ConceptRelationsGraph object
        """
        return self._client.get_concept_graph(
            concept_id=concept_id,
            depth=depth,
            zoom_level=zoom_level,
        )

    def summary(self, concept_id: int) -> Dict[str, Any]:
        """
        Get a comprehensive summary for a concept.

        This aggregates details, relationships, and graph information.

        Args:
            concept_id: The concept ID to summarize

        Returns:
            Dictionary containing details, relationships, and graph
        """
        details = self.details(concept_id)
        relationships = self.relationships(concept_id)
        graph = self.graph(concept_id)

        return {
            "details": details,
            "relationships": relationships,
            "graph": graph,
        }

    @staticmethod
    def capabilities() -> Dict[str, Dict[str, Any]]:
        """
        Get machine-readable manifest of all supported verbs.

        Returns:
            Dictionary containing capabilities information
        """
        return {
            "search": {
                "endpoint": "/concepts",
                "auth": "anonymous|bearer",
                "outputs": ["models", "list", "dataframe", "json", "yaml", "csv"],
            },
            "details": {
                "endpoint": "/concepts/{id}",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"],
            },
            "relationships": {
                "endpoint": "/concepts/{id}/relationships",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"],
            },
            "graph": {
                "endpoint": "/concepts/{id}/relations",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"],
            },
            "summary": {
                "composed_of": ["details", "relationships", "graph"],
                "outputs": ["dict"],
            },
        }


# Type hint for return annotation - needed at the end to avoid circular imports
# This import is used for type hints only, which is why it's placed at the bottom
from .search_result import SearchResult  # noqa: E402

```

### File: `athena_client/athena_client/async_client.py`
<a name="athena_client-athena_client-async_clientpy"></a>
```python
"""
Asynchronous Athena API client implementation.

This module provides an asynchronous client for the Athena API using httpx.
"""

import json
import logging
from typing import Any, Dict, Optional, Union, cast
from urllib.parse import urljoin

import backoff

try:
    import httpx
except ImportError as err:
    raise ImportError(
        "httpx is required for the async client. "
        "Install with 'pip install \"athena-client[async]\"'"
    ) from err

from .auth import build_headers
from .exceptions import AthenaError, ClientError, NetworkError, ServerError
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship
from .settings import get_settings

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """
    Asynchronous HTTP client for making requests to the Athena API.

    Features:
    - Automatic retry with exponential backoff
    - Custom timeout handling
    - Authentication header generation
    - Error handling and mapping to typed exceptions
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the async HTTP client with configuration.

        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        settings = get_settings()

        # Use provided values or fall back to settings
        self.base_url = base_url or settings.ATHENA_BASE_URL

        # Set up token and HMAC if provided
        if token is not None:
            settings.ATHENA_TOKEN = token
        if client_id is not None:
            settings.ATHENA_CLIENT_ID = client_id
        if private_key is not None:
            settings.ATHENA_PRIVATE_KEY = private_key

        self.timeout = timeout or settings.ATHENA_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.ATHENA_MAX_RETRIES
        self.backoff_factor = backoff_factor or settings.ATHENA_BACKOFF_FACTOR

        # Create httpx client
        self.client = httpx.AsyncClient(timeout=self.timeout)

    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.

        Args:
            path: API endpoint path

        Returns:
            Full URL
        """
        return urljoin(self.base_url, path)

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response from httpx

        Returns:
            Parsed JSON response

        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            else:
                raise
        except httpx.DecodingError as e:
            raise AthenaError(f"Invalid JSON response: {e}") from e

    @backoff.on_exception(
        backoff.expo,
        (httpx.TimeoutException, httpx.ConnectError),
        max_tries=3,
        factor=0.3,
    )
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make an HTTP request to the Athena API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object

        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        url = self._build_url(path)
        body_bytes = b""

        # Convert data to JSON bytes if provided
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")

        # Build authentication headers
        headers = build_headers(method, url, body_bytes)

        # Add Content-Type header if sending data
        if data is not None:
            headers["Content-Type"] = "application/json"

        # Generate a correlation ID for logging
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(f"[{correlation_id}] {method} {url}")

        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                content=body_bytes if data is not None else None,
                headers=headers,
                timeout=self.timeout,
            )

            logger.debug(
                f"[{correlation_id}] {response.status_code} {response.reason_phrase}"
            )

            if raw_response:
                return response

            return await self._handle_response(response)

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.warning(f"[{correlation_id}] Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make a GET request to the Athena API.

        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return await self.request("GET", path, params=params, raw_response=raw_response)

    async def post(
        self,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make a POST request to the Athena API.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return await self.request(
            "POST", path, data=data, params=params, raw_response=raw_response
        )


class AthenaAsyncClient:
    """
    Asynchronous client for the Athena API.

    This class provides asynchronous access to all Athena API endpoints
    with minimal abstraction, returning parsed Pydantic models.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the async Athena client with configuration.

        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.http = AsyncHttpClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    async def search_concepts(
        self,
        query: str = "",
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for concepts in the Athena vocabulary.

        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status

        Returns:
            Raw API response data
        """
        params: Dict[str, Any] = {"pageSize": page_size, "page": page}

        # Add query if provided
        if query:
            params["query"] = query

        # Add filters if provided
        if exact:
            params["exact"] = exact
        if fuzzy:
            params["fuzzy"] = str(fuzzy).lower()
        if wildcard:
            params["wildcard"] = wildcard
        if domain:
            params["domain"] = domain
        if vocabulary:
            params["vocabulary"] = vocabulary
        if standard_concept:
            params["standardConcept"] = standard_concept

        # If boosts provided, use debug endpoint and include boosts in request
        if boosts or debug:
            response = await self.http.post(
                "/concepts",
                data={"boosts": boosts} if boosts else {},
                params=params,
            )
            return cast(Dict[str, Any], response)

        # Otherwise use standard GET endpoint
        response = await self.http.get("/concepts", params=params)
        return cast(Dict[str, Any], response)

    async def get_concept_details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.

        Args:
            concept_id: The concept ID to get details for

        Returns:
            ConceptDetails object
        """
        response = await self.http.get(f"/concepts/{concept_id}")
        data = cast(Dict[str, Any], response)
        return ConceptDetails.model_validate(data)

    async def get_concept_relationships(
        self,
        concept_id: int,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.

        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts

        Returns:
            ConceptRelationship object
        """
        params: Dict[str, Any] = {}

        if relationship_id:
            params["relationshipId"] = relationship_id
        if only_standard:
            params["standardConcepts"] = "true"

        response = await self.http.get(
            f"/concepts/{concept_id}/relationships", params=params
        )
        data = cast(Dict[str, Any], response)
        return ConceptRelationship.model_validate(data)

    async def get_concept_graph(
        self,
        concept_id: int,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.

        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph

        Returns:
            ConceptRelationsGraph object
        """
        params = {"depth": depth, "zoomLevel": zoom_level}
        response = await self.http.get(
            f"/concepts/{concept_id}/relations", params=params
        )
        data = cast(Dict[str, Any], response)
        return ConceptRelationsGraph.model_validate(data)

```

### File: `athena_client/athena_client/auth.py`
<a name="athena_client-athena_client-authpy"></a>
```python
"""
Authentication module for the Athena client.

This module handles Bearer token and HMAC authentication for the Athena API.
"""

from typing import Any, Dict

from .settings import get_settings


def build_headers(method: str, url: str, body: bytes) -> Dict[str, str]:
    """
    Build authentication headers for Athena API requests.

    If a token is supplied, adds Bearer authentication.
    If a private key is supplied, adds HMAC signature.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        body: Request body as bytes

    Returns:
        Dictionary of headers to add to the request
    """
    s = get_settings()
    if s.ATHENA_TOKEN is None:
        return {}

    hdrs = {
        "X-Athena-Auth": f"Bearer {s.ATHENA_TOKEN}",
        "X-Athena-Client-Id": s.ATHENA_CLIENT_ID or "athena-client",
    }

    if s.ATHENA_PRIVATE_KEY:
        # Import here for optional dependency
        try:
            from base64 import b64encode
            from datetime import datetime

            from cryptography.hazmat.primitives import hashes, serialization

            nonce = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            to_sign = f"{method}\n{url}\n\n{nonce}\n{body.decode()}"
            key = serialization.load_pem_private_key(
                s.ATHENA_PRIVATE_KEY.encode(), password=None
            )
            signing_key: Any = key
            sig = signing_key.sign(to_sign.encode(), hashes.SHA256())
            hdrs.update(
                {"X-Athena-Nonce": nonce, "X-Athena-Hmac": b64encode(sig).decode()}
            )
        except ImportError:
            import logging

            logging.warning(
                "cryptography package is required for HMAC signing. "
                "Install with 'pip install \"athena-client[crypto]\"'"
            )

    return hdrs

```

### File: `athena_client/athena_client/cli.py`
<a name="athena_client-athena_client-clipy"></a>
```python
"""
Command-line interface for the Athena client.

This module provides a CLI for interacting with the Athena API.
"""

import json
import sys
from typing import Any, Optional

try:
    import click
except ImportError:
    click = None  # type: ignore
    print(
        "The 'click' package is required for the CLI. "
        "Install with 'pip install \"athena-client[cli]\"'"
    )
    sys.exit(1)

try:
    import rich
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
except ImportError:
    rich = None  # type: ignore
    Console = None  # type: ignore
    Syntax = None  # type: ignore
    Table = None  # type: ignore

from . import Athena, __version__


def _create_client(
    base_url: Optional[str],
    token: Optional[str],
    timeout: Optional[int],
    retries: Optional[int],
) -> Athena:
    """
    Create an Athena client with the given parameters.

    Args:
        base_url: Base URL for the Athena API
        token: Bearer token for authentication
        timeout: HTTP timeout in seconds
        retries: Maximum number of retry attempts

    Returns:
        Athena client
    """
    return Athena(
        base_url=base_url,
        token=token,
        timeout=timeout,
        max_retries=retries,
    )


def _format_output(data: object, output: str, console: Any = None) -> None:
    """
    Format and print data based on the requested output format.

    Args:
        data: Data to format and print
        output: Output format (json, yaml, table, pretty)
        console: Rich console for pretty printing
    """
    if output == "json":
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))
    elif output == "yaml":
        try:
            import yaml
        except ImportError:
            print(
                "The 'pyyaml' package is required for YAML output. "
                "Install with 'pip install \"athena-client[yaml]\"'"
            )
            sys.exit(1)

        print(yaml.dump(data))
    elif output == "table" and console is not None and rich is not None:
        if hasattr(data, "to_list"):
            # Handle SearchResult
            results = data.to_list()
            if not results:
                console.print("[yellow]No results found[/yellow]")
                return

            table = Table(title="Athena Concepts")

            # Add columns
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Code", style="magenta")
            table.add_column("Vocabulary", style="blue")
            table.add_column("Domain", style="yellow")
            table.add_column("Class", style="red")

            # Add rows
            for item in results:
                table.add_row(
                    str(item["id"]),
                    item["name"],
                    item["concept_code"],
                    item["vocabulary"]["name"],
                    item["domain"]["name"],
                    item["concept_class"]["name"],
                )

            console.print(table)
        else:
            # Just pretty-print JSON for other data types
            syntax = Syntax(
                json.dumps(data, indent=2, default=str),
                "json",
                theme="monokai",
                word_wrap=True,
            )
            console.print(syntax)
    elif output == "pretty" and console is not None and rich is not None:
        # Use rich's pretty printing
        console.print(data)
    else:
        # Fall back to regular JSON
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))


@click.group()
@click.version_option(__version__)
@click.option(
    "--base-url",
    envvar="ATHENA_BASE_URL",
    help="Base URL for the Athena API",
)
@click.option(
    "--token",
    envvar="ATHENA_TOKEN",
    help="Bearer token for authentication",
)
@click.option(
    "--timeout",
    type=int,
    envvar="ATHENA_TIMEOUT_SECONDS",
    help="HTTP timeout in seconds",
)
@click.option(
    "--retries",
    type=int,
    envvar="ATHENA_MAX_RETRIES",
    help="Maximum number of retry attempts",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "yaml", "table", "pretty"]),
    default="table",
    help="Output format",
)
@click.pass_context
def cli(
    ctx: Any,
    base_url: Optional[str],
    token: Optional[str],
    timeout: Optional[int],
    retries: Optional[int],
    output: str,
) -> None:
    """Athena Client CLI - Interact with the OHDSI Athena API."""
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url
    ctx.obj["token"] = token
    ctx.obj["timeout"] = timeout
    ctx.obj["retries"] = retries
    ctx.obj["output"] = output

    # Set up rich console if available
    if rich is not None:
        ctx.obj["console"] = Console()
    else:
        ctx.obj["console"] = None


@cli.command()
@click.argument("query")
@click.option("--fuzzy/--no-fuzzy", default=False, help="Enable fuzzy matching")
@click.option("--page-size", type=int, default=20, help="Number of results per page")
@click.option("--page", type=int, default=0, help="Page number (0-indexed)")
@click.option("--domain", help="Filter by domain")
@click.option("--vocabulary", help="Filter by vocabulary")
@click.pass_context
def search(
    ctx: Any,
    query: str,
    fuzzy: bool,
    page_size: int,
    page: int,
    domain: Optional[str],
    vocabulary: Optional[str],
) -> None:
    """Search for concepts in the Athena vocabulary."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )

    results = client.search(
        query,
        fuzzy=fuzzy,
        page_size=page_size,
        page=page,
        domain=domain,
        vocabulary=vocabulary,
    )

    # Get the appropriate output based on the format
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = results.to_json()
    elif ctx.obj["output"] == "yaml":
        output_data = results.to_yaml()
    else:
        output_data = results

    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.pass_context
def details(ctx: Any, concept_id: int) -> None:
    """Get detailed information for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )

    result = client.details(concept_id)
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml

        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()

    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.option("--relationship-id", help="Filter by relationship type")
@click.option(
    "--only-standard/--all", default=False, help="Only include standard concepts"
)
@click.pass_context
def relationships(
    ctx: Any,
    concept_id: int,
    relationship_id: Optional[str],
    only_standard: bool,
) -> None:
    """Get relationships for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )

    result = client.relationships(
        concept_id,
        relationship_id=relationship_id,
        only_standard=only_standard,
    )
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml

        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()

    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.option("--depth", type=int, default=10, help="Maximum depth of relationships")
@click.option("--zoom-level", type=int, default=4, help="Zoom level for the graph")
@click.pass_context
def graph(ctx: Any, concept_id: int, depth: int, zoom_level: int) -> None:
    """Get relationship graph for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )

    result = client.graph(
        concept_id,
        depth=depth,
        zoom_level=zoom_level,
    )
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml

        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()

    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.pass_context
def summary(ctx: Any, concept_id: int) -> None:
    """Get a comprehensive summary for a concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )

    result = client.summary(concept_id)

    # Convert Pydantic models to dicts for serialization
    output_data = {
        "details": result["details"].model_dump(),
        "relationships": result["relationships"].model_dump(),
        "graph": result["graph"].model_dump(),
    }

    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command(name="caps")
@click.pass_context
def capabilities(ctx: Any) -> None:
    """List capabilities of the Athena client."""
    caps = Athena.capabilities()
    _format_output(caps, ctx.obj["output"], ctx.obj.get("console"))


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})  # pylint: disable=unexpected-keyword-arg


if __name__ == "__main__":
    main()

```

### File: `athena_client/athena_client/client.py`
<a name="athena_client-athena_client-clientpy"></a>
```python
"""
Athena API client implementation.

This module provides the core synchronous client for the Athena API.
"""

from typing import Any, Dict, Optional, cast

from .http import HttpClient
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship


class AthenaClient:
    """
    Core synchronous client for the Athena API.

    This class provides direct access to all Athena API endpoints
    with minimal abstraction, returning parsed Pydantic models.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the Athena client with configuration.

        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.http = HttpClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

    def search_concepts(
        self,
        query: str = "",
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for concepts in the Athena vocabulary.

        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status

        Returns:
            Raw API response data
        """
        params: Dict[str, Any] = {"pageSize": page_size, "page": page}

        # Add query if provided
        if query:
            params["query"] = query

        # Add filters if provided
        if exact:
            params["exact"] = exact
        if fuzzy:
            params["fuzzy"] = str(fuzzy).lower()
        if wildcard:
            params["wildcard"] = wildcard
        if domain:
            params["domain"] = domain
        if vocabulary:
            params["vocabulary"] = vocabulary
        if standard_concept:
            params["standardConcept"] = standard_concept

        # If boosts provided, use debug endpoint and include boosts in request
        if boosts or debug:
            return cast(
                Dict[str, Any],
                self.http.post(
                    "/concepts",
                    data={"boosts": boosts} if boosts else {},
                    params=params,
                ),
            )

        # Otherwise use standard GET endpoint
        return cast(Dict[str, Any], self.http.get("/concepts", params=params))

    def get_concept_details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.

        Args:
            concept_id: The concept ID to get details for

        Returns:
            ConceptDetails object
        """
        data = self.http.get(f"/concepts/{concept_id}")
        return ConceptDetails.model_validate(data)

    def get_concept_relationships(
        self,
        concept_id: int,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.

        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts

        Returns:
            ConceptRelationship object
        """
        params: Dict[str, Any] = {}

        if relationship_id:
            params["relationshipId"] = relationship_id
        if only_standard:
            params["standardConcepts"] = "true"

        data = self.http.get(f"/concepts/{concept_id}/relationships", params=params)
        return ConceptRelationship.model_validate(data)

    def get_concept_graph(
        self,
        concept_id: int,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.

        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph

        Returns:
            ConceptRelationsGraph object
        """
        params = {"depth": depth, "zoomLevel": zoom_level}
        data = self.http.get(f"/concepts/{concept_id}/relations", params=params)
        return ConceptRelationsGraph.model_validate(data)

```

### File: `athena_client/athena_client/exceptions.py`
<a name="athena_client-athena_client-exceptionspy"></a>
```python
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

```

### File: `athena_client/athena_client/http.py`
<a name="athena_client-athena_client-httppy"></a>
```python
"""
HTTP client implementation for Athena API.

This module provides HTTP clients for making requests to the Athena API,
with features like retry, backoff, and timeout handling.
"""

import json
import logging
from typing import Any, Dict, Optional, TypeVar, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import build_headers
from .exceptions import AthenaError, ClientError, NetworkError, ServerError
from .settings import get_settings

# Type variable for generic response
T = TypeVar("T")

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Synchronous HTTP client for making requests to the Athena API.

    Features:
    - Automatic retry with exponential backoff
    - Custom timeout handling
    - Authentication header generation
    - Error handling and mapping to typed exceptions
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the HTTP client with configuration.

        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        settings = get_settings()

        # Use provided values or fall back to settings
        self.base_url = base_url or settings.ATHENA_BASE_URL

        # Set up token and HMAC if provided
        if token is not None:
            settings.ATHENA_TOKEN = token
        if client_id is not None:
            settings.ATHENA_CLIENT_ID = client_id
        if private_key is not None:
            settings.ATHENA_PRIVATE_KEY = private_key

        self.timeout = timeout or settings.ATHENA_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.ATHENA_MAX_RETRIES
        self.backoff_factor = backoff_factor or settings.ATHENA_BACKOFF_FACTOR

        # Create session with retry configuration
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create and configure a requests Session with retry logic.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.

        Args:
            path: API endpoint path

        Returns:
            Full URL
        """
        return urljoin(self.base_url, path)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: HTTP response from requests

        Returns:
            Parsed JSON response

        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            else:
                raise
        except requests.exceptions.JSONDecodeError as e:
            raise AthenaError(f"Invalid JSON response: {e}") from e

    def request(
        self,
        method: str,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make an HTTP request to the Athena API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object

        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        url = self._build_url(path)
        body_bytes = b""

        # Convert data to JSON bytes if provided
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")

        # Build authentication headers
        headers = build_headers(method, url, body_bytes)

        # Add Content-Type header if sending data
        if data is not None:
            headers["Content-Type"] = "application/json"

        # Generate a correlation ID for logging
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(f"[{correlation_id}] {method} {url}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=body_bytes if data is not None else None,
                headers=headers,
                timeout=self.timeout,
            )

            logger.debug(f"[{correlation_id}] {response.status_code} {response.reason}")

            if raw_response:
                return response

            return self._handle_response(response)

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"[{correlation_id}] Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e

    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a GET request to the Athena API.

        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return self.request("GET", path, params=params, raw_response=raw_response)

    def post(
        self,
        path: str,
        data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a POST request to the Athena API.

        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            raw_response: Whether to return the raw response object

        Returns:
            Parsed JSON response or raw Response object
        """
        return self.request(
            "POST", path, data=data, params=params, raw_response=raw_response
        )

```

### File: `athena_client/athena_client/query.py`
<a name="athena_client-athena_client-querypy"></a>
```python
"""
Query DSL for building complex Athena queries.

This module provides a Query DSL that allows for building complex queries
using a fluent interface and operator overloading.
"""

from typing import Any, Dict, Optional


class Q:
    """
    Query DSL for building complex Athena queries.

    Usage:
        q = Q.term("diabetes")
        q = Q.phrase("heart attack")
        q = Q.exact('"Myocardial Infarction"')
        q = Q.wildcard("aspir*")

        # Combine with operators
        q = Q.term("diabetes") & Q.term("type 2")  # AND
        q = Q.term("heart") | Q.term("cardiac")    # OR
        q = -Q.term("chronic")                     # NOT

        # Apply modifiers
        q = Q.term("aspirin").fuzzy(0.8)

        # Get boosts for the API
        boosts = q.to_boosts()
    """

    def __init__(self, query_type: str, value: str, **kwargs: Any) -> None:
        """
        Initialize a query object.

        Args:
            query_type: Type of query (term, phrase, exact, wildcard)
            value: Query value
            **kwargs: Additional options
        """
        self.query_type = query_type
        self.value = value
        self.options = kwargs
        self.operator: Optional[str] = None
        self.left: Optional["Q"] = None
        self.right: Optional["Q"] = None

    @classmethod
    def term(cls, value: str) -> "Q":
        """
        Create a term query.

        Args:
            value: Term to search for

        Returns:
            Query object
        """
        return cls("term", value)

    @classmethod
    def phrase(cls, value: str) -> "Q":
        """
        Create a phrase query.

        Args:
            value: Phrase to search for

        Returns:
            Query object
        """
        return cls("phrase", value)

    @classmethod
    def exact(cls, value: str) -> "Q":
        """
        Create an exact match query.

        Args:
            value: Exact phrase to search for (should be in quotes)

        Returns:
            Query object
        """
        if not value.startswith('"') or not value.endswith('"'):
            value = f'"{value}"'
        return cls("exact", value)

    @classmethod
    def wildcard(cls, value: str) -> "Q":
        """
        Create a wildcard query.

        Args:
            value: Wildcard pattern (e.g., "aspir*")

        Returns:
            Query object
        """
        if not value.endswith("*"):
            value = f"{value}*"
        return cls("wildcard", value)

    def fuzzy(self, ratio: float = 0.7) -> "Q":
        """
        Apply fuzzy matching to the query.

        Args:
            ratio: Fuzzy match ratio (0.0 - 1.0)

        Returns:
            Query object with fuzzy matching
        """
        self.options["fuzzy"] = ratio
        return self

    def __and__(self, other: "Q") -> "Q":
        """
        Combine with AND operator.

        Args:
            other: Another Q object

        Returns:
            New Q object representing the AND condition
        """
        result = Q("compound", "")
        result.operator = "AND"
        result.left = self
        result.right = other
        return result

    def __or__(self, other: "Q") -> "Q":
        """
        Combine with OR operator.

        Args:
            other: Another Q object

        Returns:
            New Q object representing the OR condition
        """
        result = Q("compound", "")
        result.operator = "OR"
        result.left = self
        result.right = other
        return result

    def __neg__(self) -> "Q":
        """
        Apply NOT operator.

        Returns:
            New Q object representing the NOT condition
        """
        result = Q("compound", "")
        result.operator = "NOT"
        result.right = self
        return result

    def to_boosts(self) -> Dict[str, Any]:
        """
        Convert the query to a boosts dictionary for the Athena API.

        Returns:
            Dictionary with query boosts
        """
        if self.query_type == "compound":
            if self.operator == "AND":
                assert self.left is not None and self.right is not None
                boosts_left = self.left.to_boosts()
                boosts_right = self.right.to_boosts()
                # Merge the boosts with AND logic
                return {
                    "filter": {
                        "bool": {
                            "must": [
                                boosts_left.get("filter", {}),
                                boosts_right.get("filter", {}),
                            ]
                        }
                    }
                }
            elif self.operator == "OR":
                assert self.left is not None and self.right is not None
                boosts_left = self.left.to_boosts()
                boosts_right = self.right.to_boosts()
                # Merge the boosts with OR logic
                return {
                    "filter": {
                        "bool": {
                            "should": [
                                boosts_left.get("filter", {}),
                                boosts_right.get("filter", {}),
                            ]
                        }
                    }
                }
            elif self.operator == "NOT":
                assert self.right is not None
                boosts_right = self.right.to_boosts()
                # Apply NOT logic
                return {
                    "filter": {"bool": {"must_not": [boosts_right.get("filter", {})]}}
                }

        # Handle basic query types
        query_dict: Dict[str, Any] = {}

        if self.query_type == "term":
            query_dict["query"] = self.value
            query_dict["fields"] = [
                "name^10",
                "synonyms^5",
                "definition^3",
                "concept_code",
            ]
        elif self.query_type == "phrase":
            query_dict["query"] = f'"{self.value}"'
            query_dict["fields"] = ["name^10", "synonyms^5", "definition^3"]
        elif self.query_type == "exact":
            query_dict["query"] = self.value
            query_dict["fields"] = ["concept_code^20", "name.exact^15"]
        elif self.query_type == "wildcard":
            query_dict["query"] = self.value
            query_dict["fields"] = ["name^10", "synonyms^5"]

        # Apply fuzzy if requested
        if "fuzzy" in self.options:
            query_dict["fuzziness"] = self.options["fuzzy"]

        return {"filter": {"query_string": query_dict}}

```

### File: `athena_client/athena_client/search_result.py`
<a name="athena_client-athena_client-search_resultpy"></a>
```python
"""
SearchResult formatter for Athena search results.

This module provides a class for handling and formatting search results
from the Athena API into various output formats.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union

from .exceptions import ValidationError
from .models import Concept, ConceptSearchResponse

# Optional imports
pd = None
yaml = None


class SearchResult:
    """
    Formatter for search results from the Athena API.

    This class provides methods to convert search results into various formats:
    - Pydantic models (all, top)
    - Python dictionaries (to_list)
    - pandas DataFrames (to_df)
    - JSON (to_json)
    - YAML (to_yaml)
    - CSV (to_csv)
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize with API response data.

        Args:
            data: Raw API response from search endpoint

        Raises:
            ValidationError: If the data cannot be parsed
        """
        try:
            self._response = ConceptSearchResponse.model_validate(data)
        except Exception as e:
            raise ValidationError(f"Failed to parse search results: {e}") from e

    def all(self) -> List[Concept]:
        """
        Get all concepts as Pydantic objects.

        Returns:
            List of Concept objects
        """
        return self._response.content

    def top(self, n: int = 10) -> List[Concept]:
        """
        Get top N concepts as Pydantic objects.

        Args:
            n: Number of concepts to return

        Returns:
            List of top N Concept objects
        """
        return self._response.content[:n]

    def to_models(self) -> List[Concept]:
        """
        Alias for all().

        Returns:
            List of Concept objects
        """
        return self.all()

    def to_list(self) -> List[Dict[str, Any]]:
        """
        Get concepts as list of dictionaries.

        Returns:
            List of concept dictionaries
        """
        return [concept.model_dump() for concept in self.all()]

    def to_df(self) -> Any:
        """
        Get concepts as pandas DataFrame.

        Returns:
            pandas DataFrame

        Raises:
            ImportError: If pandas is not installed
        """
        global pd
        if pd is None:
            try:
                import pandas as pd_mod

                pd = pd_mod
            except ImportError as err:
                raise ImportError(
                    "pandas is required for DataFrame output. "
                    "Install with 'pip install \"athena-client[pandas]\"'"
                ) from err

        return pd.DataFrame(self.to_list())

    def to_json(self, indent: int = 2) -> str:
        """
        Get concepts as JSON string.

        Args:
            indent: Indentation level

        Returns:
            JSON string
        """
        return json.dumps(self.to_list(), indent=indent)

    def to_yaml(self) -> str:
        """
        Get concepts as YAML string.

        Returns:
            YAML string

        Raises:
            ImportError: If PyYAML is not installed
        """
        global yaml
        if yaml is None:
            try:
                import yaml as yaml_mod

                yaml = yaml_mod
            except ImportError as err:
                raise ImportError(
                    "PyYAML is required for YAML output. "
                    "Install with 'pip install \"athena-client[yaml]\"'"
                ) from err

        return yaml.dump(self.to_list())

    def to_csv(self, path: Union[str, Path]) -> None:
        """
        Write concepts to CSV file.

        Args:
            path: File path to write CSV to

        Raises:
            ImportError: If pandas is not installed
        """
        df = self.to_df()  # This will raise ImportError if pandas is missing
        df.to_csv(path, index=False)

    def __len__(self) -> int:
        """
        Get the number of results.

        Returns:
            Number of concepts
        """
        return len(self._response.content)

    def __getitem__(self, idx: int) -> Concept:
        """
        Get a specific concept by index.

        Args:
            idx: Index of the concept

        Returns:
            Concept at the given index
        """
        return self._response.content[idx]

    @property
    def total(self) -> int:
        """
        Get the total number of results.

        Returns:
            Total number of results
        """
        return self._response.total_elements

    @property
    def page(self) -> int:
        """
        Get the current page number.

        Returns:
            Current page number
        """
        return self._response.number

    @property
    def pages(self) -> int:
        """
        Get the total number of pages.

        Returns:
            Total number of pages
        """
        return self._response.total_pages

```

### File: `athena_client/athena_client/settings.py`
<a name="athena_client-athena_client-settingspy"></a>
```python
"""
Settings module for the Athena client.

This module provides configuration settings loaded from environment variables
or .env files using pydantic-settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """
    Configuration settings for the Athena client.

    Settings can be provided via environment variables, .env file, or defaults.
    """

    ATHENA_BASE_URL: str = "https://athena.ohdsi.org/api/v1"
    ATHENA_TOKEN: Optional[str] = None
    ATHENA_CLIENT_ID: Optional[str] = None
    ATHENA_PRIVATE_KEY: Optional[str] = None
    ATHENA_TIMEOUT_SECONDS: int = 10
    ATHENA_MAX_RETRIES: int = 3
    ATHENA_BACKOFF_FACTOR: float = 0.3

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


@lru_cache
def get_settings() -> _Settings:
    """
    Get the settings singleton.

    Returns:
        Cached instance of _Settings.
    """
    return _Settings()  # cached singleton

```

## Folder: athena_client/utils

### File: `athena_client/athena_client/utils/__init__.py`
<a name="athena_client-athena_client-utils-__init__py"></a>
```python
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

```

## Folder: athena_client/models

### File: `athena_client/athena_client/models/__init__.py`
<a name="athena_client-athena_client-models-__init__py"></a>
```python
"""
Pydantic models for Athena API responses.

This module defines Pydantic models for the various responses from the Athena API.
"""

from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Union, cast

import orjson
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


def _json_dumps(value: Any, *, default: Any) -> str:
    """Serialize to JSON using orjson."""
    return orjson.dumps(value, default=default).decode()


class BaseModel(PydanticBaseModel):
    """Project-wide Pydantic base model using orjson."""

    model_config: ClassVar[ConfigDict] = cast(
        ConfigDict,
        {
            "populate_by_name": True,
            "extra": "ignore",
        },
    )

    def model_dump_json(self, **kwargs: Any) -> str:
        """Serialize model to JSON using orjson."""
        return orjson.dumps(self.model_dump(**kwargs)).decode()

    @classmethod
    def model_validate_json(
        cls: type["BaseModel"], json_data: Union[str, bytes], **kwargs: Any
    ) -> "BaseModel":
        """Deserialize model from JSON using orjson."""
        return cls.model_validate(orjson.loads(json_data), **kwargs)


class Domain(BaseModel):
    """Domain information for a concept."""

    id: int = Field(..., description="Domain ID")
    name: str = Field(..., description="Domain name")


class Vocabulary(BaseModel):
    """Vocabulary information for a concept."""

    id: str = Field(..., description="Vocabulary ID")
    name: str = Field(..., description="Vocabulary name")


class ConceptClass(BaseModel):
    """Concept class information."""

    id: str = Field(..., description="Concept class ID")
    name: str = Field(..., description="Concept class name")


class ConceptType(str, Enum):
    """Concept standard type."""

    STANDARD = "S"
    CLASSIFICATION = "C"
    NON_STANDARD = ""


class Concept(BaseModel):
    """Basic concept information returned in search results."""

    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain_id: str = Field(..., description="Domain ID")
    vocabulary_id: str = Field(..., description="Vocabulary ID")
    concept_class_id: str = Field(..., description="Concept class ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    concept_code: str = Field(..., description="Concept code")
    invalid_reason: Optional[str] = Field(None, description="Invalid reason")
    domain: Domain = Field(..., description="Domain object")
    vocabulary: Vocabulary = Field(..., description="Vocabulary object")
    concept_class: ConceptClass = Field(..., description="Concept class object")
    valid_start_date: str = Field(..., description="Valid start date")
    valid_end_date: str = Field(..., description="Valid end date")


class ConceptSearchResponse(BaseModel):
    """Response from the /concepts search endpoint."""

    content: List[Concept] = Field(..., description="List of concept results")
    pageable: Dict[str, Any] = Field(..., description="Pagination information")
    total_elements: int = Field(
        ..., description="Total number of results", alias="totalElements"
    )
    last: bool = Field(..., description="Whether this is the last page")
    total_pages: int = Field(
        ..., description="Total number of pages", alias="totalPages"
    )
    sort: Dict[str, Any] = Field(..., description="Sort information")
    first: bool = Field(..., description="Whether this is the first page")
    size: int = Field(..., description="Page size")
    number: int = Field(..., description="Page number")
    number_of_elements: int = Field(
        ..., description="Number of elements in this page", alias="numberOfElements"
    )
    empty: bool = Field(..., description="Whether the result is empty")


class ConceptDetails(BaseModel):
    """Detailed concept information from the /concepts/{id} endpoint."""

    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain_id: str = Field(..., description="Domain ID")
    vocabulary_id: str = Field(..., description="Vocabulary ID")
    concept_class_id: str = Field(..., description="Concept class ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    concept_code: str = Field(..., description="Concept code")
    invalid_reason: Optional[str] = Field(None, description="Invalid reason")
    domain: Domain = Field(..., description="Domain object")
    vocabulary: Vocabulary = Field(..., description="Vocabulary object")
    concept_class: ConceptClass = Field(..., description="Concept class object")
    valid_start_date: str = Field(..., description="Valid start date")
    valid_end_date: str = Field(..., description="Valid end date")
    # Additional fields specific to details
    synonyms: Optional[List[str]] = Field(None, description="Concept synonyms")
    additional_information: Optional[Dict[str, Any]] = Field(
        None, description="Additional information"
    )


class RelationshipItem(BaseModel):
    """Information about a relationship between concepts."""

    relationship_id: str = Field(..., description="Relationship ID")
    relationship_name: str = Field(..., description="Relationship name")
    relationship_concept_id: int = Field(..., description="Relationship concept ID")


class ConceptRelationship(BaseModel):
    """Response from the /concepts/{id}/relationships endpoint."""

    concept_id: int = Field(..., description="Concept ID")
    relationships: List[RelationshipItem] = Field(
        ..., description="List of relationships"
    )


class GraphNode(BaseModel):
    """Node in the concept relationship graph."""

    id: int = Field(..., description="Node ID")
    name: str = Field(..., description="Node name")
    concept_id: int = Field(..., description="Concept ID")
    domain_id: str = Field(..., description="Domain ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )


class GraphEdge(BaseModel):
    """Edge in the concept relationship graph."""

    source: int = Field(..., description="Source node ID")
    target: int = Field(..., description="Target node ID")
    relationship_id: str = Field(..., description="Relationship ID")


class ConceptRelationsGraph(BaseModel):
    """Response from the /concepts/{id}/relations endpoint."""

    nodes: List[GraphNode] = Field(..., description="Graph nodes")
    edges: List[GraphEdge] = Field(..., description="Graph edges")


# Re-export models
__all__ = [
    "Concept",
    "ConceptClass",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
    "ConceptSearchResponse",
    "ConceptType",
    "Domain",
    "GraphEdge",
    "GraphNode",
    "RelationshipItem",
    "Vocabulary",
]

```

## Folder: .ruff_cache

## Folder: .ruff_cache/0.12.0

## Folder: .ruff_cache/0.11.10

## Folder: tests

### File: `athena_client/tests/__init__.py`
<a name="athena_client-tests-__init__py"></a>
```python
"""
Tests for the athena-client package.
"""

```

### File: `athena_client/tests/conftest.py`
<a name="athena_client-tests-conftestpy"></a>
```python
"""
Test fixtures and configuration for athena-client tests.
"""

from unittest.mock import patch

import pytest

from athena_client import Athena
from athena_client.client import AthenaClient


@pytest.fixture
def mock_http_client():
    """Mock HttpClient to avoid making real API calls."""
    with patch("athena_client.client.HttpClient") as mock:
        yield mock


@pytest.fixture
def athena_client(mock_http_client):
    """Get a mocked Athena client."""
    client = AthenaClient()
    return client


@pytest.fixture
def athena_facade(mock_http_client):
    """Get a mocked Athena facade."""
    facade = Athena()
    return facade

```

### File: `athena_client/tests/test_query.py`
<a name="athena_client-tests-test_querypy"></a>
```python
"""
Tests for the Query DSL.
"""

from athena_client.query import Q


def test_term_query():
    """Test basic term query construction."""
    q = Q.term("diabetes")
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == "diabetes"
    assert "name^10" in boosts["filter"]["query_string"]["fields"]
    assert "synonyms^5" in boosts["filter"]["query_string"]["fields"]


def test_phrase_query():
    """Test phrase query construction."""
    q = Q.phrase("heart attack")
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == '"heart attack"'


def test_exact_query():
    """Test exact query construction."""
    q = Q.exact('"Myocardial Infarction"')
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == '"Myocardial Infarction"'
    assert "concept_code^20" in boosts["filter"]["query_string"]["fields"]
    assert "name.exact^15" in boosts["filter"]["query_string"]["fields"]


def test_wildcard_query():
    """Test wildcard query construction."""
    q = Q.wildcard("aspir*")
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == "aspir*"


def test_fuzzy_modifier():
    """Test fuzzy modifier."""
    q = Q.term("aspirin").fuzzy(0.8)
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["fuzziness"] == 0.8


def test_and_operator():
    """Test AND operator."""
    q = Q.term("diabetes") & Q.term("type 2")
    boosts = q.to_boosts()

    assert "must" in boosts["filter"]["bool"]
    assert len(boosts["filter"]["bool"]["must"]) == 2


def test_or_operator():
    """Test OR operator."""
    q = Q.term("heart") | Q.term("cardiac")
    boosts = q.to_boosts()

    assert "should" in boosts["filter"]["bool"]
    assert len(boosts["filter"]["bool"]["should"]) == 2


def test_not_operator():
    """Test NOT operator."""
    q = -Q.term("chronic")
    boosts = q.to_boosts()

    assert "must_not" in boosts["filter"]["bool"]
    assert len(boosts["filter"]["bool"]["must_not"]) == 1


def test_complex_query():
    """Test complex query with multiple operators."""
    q = (Q.term("diabetes") & Q.term("type 2")) | Q.exact('"diabetic nephropathy"')
    boosts = q.to_boosts()

    assert "should" in boosts["filter"]["bool"]

```

### File: `athena_client/tests/test_search_result.py`
<a name="athena_client-tests-test_search_resultpy"></a>
```python
"""
Tests for the SearchResult class.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from athena_client.exceptions import ValidationError
from athena_client.search_result import SearchResult


@pytest.fixture
def mock_search_response():
    """Sample search response fixture."""
    return {
        "content": [
            {
                "id": 1127433,
                "name": "Aspirin",
                "domain_id": "Drug",
                "vocabulary_id": "RxNorm",
                "concept_class_id": "Ingredient",
                "standard_concept": "S",
                "concept_code": "1191",
                "valid_start_date": "2000-01-01",
                "valid_end_date": "2099-12-31",
                "invalid_reason": None,
                "domain": {"id": 13, "name": "Drug"},
                "vocabulary": {"id": "RxNorm", "name": "RxNorm"},
                "concept_class": {"id": "Ingredient", "name": "Ingredient"},
            }
        ],
        "pageable": {
            "sort": {"sorted": True, "unsorted": False, "empty": False},
            "pageSize": 20,
            "pageNumber": 0,
            "offset": 0,
            "paged": True,
            "unpaged": False,
        },
        "totalElements": 1,
        "last": True,
        "totalPages": 1,
        "first": True,
        "sort": {"sorted": True, "unsorted": False, "empty": False},
        "size": 20,
        "number": 0,
        "numberOfElements": 1,
        "empty": False,
    }


def test_search_result_init(mock_search_response):
    """Test SearchResult initialization."""
    result = SearchResult(mock_search_response)
    assert len(result.all()) == 1
    assert result.all()[0].name == "Aspirin"
    assert result.all()[0].id == 1127433


def test_search_result_validation_error():
    """Test validation error on bad data."""
    with pytest.raises(ValidationError):
        SearchResult({"invalid": "data"})


def test_search_result_top(mock_search_response):
    """Test top N results."""
    result = SearchResult(mock_search_response)
    assert len(result.top(1)) == 1
    assert result.top(1)[0].name == "Aspirin"


def test_search_result_to_list(mock_search_response):
    """Test conversion to list of dictionaries."""
    result = SearchResult(mock_search_response)
    data_list = result.to_list()
    assert isinstance(data_list, list)
    assert data_list[0]["name"] == "Aspirin"


def test_search_result_to_json(mock_search_response):
    """Test conversion to JSON."""
    result = SearchResult(mock_search_response)
    json_str = result.to_json()
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed[0]["name"] == "Aspirin"


def test_search_result_to_df(mock_search_response):
    """Test conversion to DataFrame."""
    mock_dataframe = MagicMock()
    mock_pandas = MagicMock()
    mock_pandas.DataFrame.return_value = mock_dataframe

    with patch.dict("sys.modules", {"pandas": mock_pandas}):
        with patch("athena_client.search_result.pd", mock_pandas):
            result = SearchResult(mock_search_response)
            result.to_df()
            mock_pandas.DataFrame.assert_called_once()


def test_search_result_to_df_missing_pandas(mock_search_response):
    """Test error when pandas is missing."""
    result = SearchResult(mock_search_response)
    with patch.dict("sys.modules", {"pandas": None}):
        with patch("athena_client.search_result.pd", None):
            with pytest.raises(ImportError):
                result.to_df()


def test_search_result_to_yaml(mock_search_response):
    """Test conversion to YAML."""
    mock_yaml = MagicMock()
    mock_yaml.dump.return_value = "yaml content"

    with patch.dict("sys.modules", {"yaml": mock_yaml}):
        with patch("athena_client.search_result.yaml", mock_yaml):
            result = SearchResult(mock_search_response)
            yaml_str = result.to_yaml()
            mock_yaml.dump.assert_called_once()
            assert yaml_str == "yaml content"


def test_search_result_to_yaml_missing_pyyaml(mock_search_response):
    """Test error when pyyaml is missing."""
    result = SearchResult(mock_search_response)
    with patch.dict("sys.modules", {"yaml": None}):
        with patch("athena_client.search_result.yaml", None):
            with pytest.raises(ImportError):
                result.to_yaml()


def test_search_result_to_csv(mock_search_response):
    """Test writing to CSV."""
    with patch("athena_client.search_result.SearchResult.to_df") as mock_to_df:
        mock_df = MagicMock()
        mock_to_df.return_value = mock_df

        result = SearchResult(mock_search_response)
        result.to_csv("test.csv")

        mock_df.to_csv.assert_called_once_with("test.csv", index=False)

```

## Folder: tests/property

### File: `athena_client/tests/property/test_query_builder.py`
<a name="athena_client-tests-property-test_query_builderpy"></a>
```python
from hypothesis import given
from hypothesis import strategies as st

from athena_client.query import Q


@given(text=st.text(min_size=1, max_size=40))
def test_phrase_builder_roundtrip(text):
    """Generated boosts should always include the raw phrase."""
    boosts = Q.phrase(text).to_boosts()
    assert text in boosts["filter"]["query_string"]["query"]


@given(prefix=st.text(min_size=1, max_size=10))
def test_wildcard_always_star(prefix):
    """Wildcard helper must append '*' if caller forgot."""
    expr = Q.wildcard(prefix)
    assert expr.value.endswith("*")

```

## Folder: tests/benchmarks

### File: `athena_client/tests/benchmarks/test_orjson.py`
<a name="athena_client-tests-benchmarks-test_orjsonpy"></a>
```python
import json

import pytest

from athena_client.models import Concept, ConceptSearchResponse

SAMPLE = ConceptSearchResponse(
    content=[
        Concept(
            id=i,
            name=f"Name {i}",
            domain_id="D",
            vocabulary_id="V",
            concept_class_id="C",
            concept_code=str(i),
            invalid_reason=None,
            domain={"id": 1, "name": "Domain"},
            vocabulary={"id": "V", "name": "Vocab"},
            concept_class={"id": "C", "name": "Class"},
            valid_start_date="2020-01-01",
            valid_end_date="2099-01-01",
            standard_concept=None,
        )
        for i in range(1000)
    ],
    pageable={},
    total_elements=1000,
    last=True,
    total_pages=1,
    sort={},
    first=True,
    size=1000,
    number=0,
    number_of_elements=1000,
    empty=False,
)


@pytest.mark.benchmark(group="json")
def test_orjson_dump(benchmark):
    benchmark(SAMPLE.model_dump_json)


@pytest.mark.benchmark(group="json")
def test_stdlib_dump(benchmark):
    benchmark(json.dumps, SAMPLE.model_dump())

```

## Folder: .hypothesis

## Folder: .hypothesis/unicode_data

## Folder: .hypothesis/unicode_data/15.1.0

## Folder: .hypothesis/constants

## Folder: .benchmarks

## Folder: .mypy_cache

## Folder: .mypy_cache/3.9

## Folder: .mypy_cache/3.9/orjson

## Folder: .mypy_cache/3.9/backoff

## Folder: .mypy_cache/3.9/mdurl

## Folder: .mypy_cache/3.9/zoneinfo

## Folder: .mypy_cache/3.9/ctypes

## Folder: .mypy_cache/3.9/httpcore

## Folder: .mypy_cache/3.9/httpcore/_backends

## Folder: .mypy_cache/3.9/httpcore/_async

## Folder: .mypy_cache/3.9/httpcore/_sync

## Folder: .mypy_cache/3.9/unittest

## Folder: .mypy_cache/3.9/h11

## Folder: .mypy_cache/3.9/dotenv

## Folder: .mypy_cache/3.9/annotated_types

## Folder: .mypy_cache/3.9/attrs

## Folder: .mypy_cache/3.9/cryptography

## Folder: .mypy_cache/3.9/cryptography/hazmat

## Folder: .mypy_cache/3.9/cryptography/hazmat/decrepit

## Folder: .mypy_cache/3.9/cryptography/hazmat/decrepit/ciphers

## Folder: .mypy_cache/3.9/cryptography/hazmat/backends

## Folder: .mypy_cache/3.9/cryptography/hazmat/backends/openssl

## Folder: .mypy_cache/3.9/cryptography/hazmat/primitives

## Folder: .mypy_cache/3.9/cryptography/hazmat/primitives/serialization

## Folder: .mypy_cache/3.9/cryptography/hazmat/primitives/ciphers

## Folder: .mypy_cache/3.9/cryptography/hazmat/primitives/asymmetric

## Folder: .mypy_cache/3.9/cryptography/hazmat/bindings

## Folder: .mypy_cache/3.9/cryptography/hazmat/bindings/_rust

## Folder: .mypy_cache/3.9/cryptography/hazmat/bindings/_rust/openssl

## Folder: .mypy_cache/3.9/cryptography/hazmat/bindings/openssl

## Folder: .mypy_cache/3.9/athena_client

## Folder: .mypy_cache/3.9/athena_client/utils

## Folder: .mypy_cache/3.9/athena_client/models

## Folder: .mypy_cache/3.9/multiprocessing

## Folder: .mypy_cache/3.9/_typeshed

## Folder: .mypy_cache/3.9/urllib

## Folder: .mypy_cache/3.9/markdown_it

## Folder: .mypy_cache/3.9/markdown_it/rules_block

## Folder: .mypy_cache/3.9/markdown_it/rules_core

## Folder: .mypy_cache/3.9/markdown_it/common

## Folder: .mypy_cache/3.9/markdown_it/rules_inline

## Folder: .mypy_cache/3.9/markdown_it/presets

## Folder: .mypy_cache/3.9/markdown_it/helpers

## Folder: .mypy_cache/3.9/zipfile

## Folder: .mypy_cache/3.9/idna

## Folder: .mypy_cache/3.9/click

## Folder: .mypy_cache/3.9/html

## Folder: .mypy_cache/3.9/numpy

## Folder: .mypy_cache/3.9/numpy/strings

## Folder: .mypy_cache/3.9/numpy/char

## Folder: .mypy_cache/3.9/numpy/core

## Folder: .mypy_cache/3.9/numpy/linalg

## Folder: .mypy_cache/3.9/numpy/ctypeslib

## Folder: .mypy_cache/3.9/numpy/ma

## Folder: .mypy_cache/3.9/numpy/_core

## Folder: .mypy_cache/3.9/numpy/_typing

## Folder: .mypy_cache/3.9/numpy/rec

## Folder: .mypy_cache/3.9/numpy/typing

## Folder: .mypy_cache/3.9/numpy/f2py

## Folder: .mypy_cache/3.9/numpy/testing

## Folder: .mypy_cache/3.9/numpy/testing/_private

## Folder: .mypy_cache/3.9/numpy/lib

## Folder: .mypy_cache/3.9/numpy/fft

## Folder: .mypy_cache/3.9/numpy/random

## Folder: .mypy_cache/3.9/numpy/matrixlib

## Folder: .mypy_cache/3.9/numpy/polynomial

## Folder: .mypy_cache/3.9/requests

## Folder: .mypy_cache/3.9/anyio

## Folder: .mypy_cache/3.9/anyio/abc

## Folder: .mypy_cache/3.9/anyio/_core

## Folder: .mypy_cache/3.9/anyio/streams

## Folder: .mypy_cache/3.9/httpx

## Folder: .mypy_cache/3.9/httpx/_transports

## Folder: .mypy_cache/3.9/sys

## Folder: .mypy_cache/3.9/certifi

## Folder: .mypy_cache/3.9/json

## Folder: .mypy_cache/3.9/sniffio

## Folder: .mypy_cache/3.9/attr

## Folder: .mypy_cache/3.9/http

## Folder: .mypy_cache/3.9/sqlite3

## Folder: .mypy_cache/3.9/concurrent

## Folder: .mypy_cache/3.9/concurrent/futures

## Folder: .mypy_cache/3.9/rich

## Folder: .mypy_cache/3.9/yaml

## Folder: .mypy_cache/3.9/os

## Folder: .mypy_cache/3.9/pydantic_settings

## Folder: .mypy_cache/3.9/pydantic_settings/sources

## Folder: .mypy_cache/3.9/pydantic_settings/sources/providers

## Folder: .mypy_cache/3.9/urllib3

## Folder: .mypy_cache/3.9/urllib3/util

## Folder: .mypy_cache/3.9/urllib3/contrib

## Folder: .mypy_cache/3.9/urllib3/http2

## Folder: .mypy_cache/3.9/importlib

## Folder: .mypy_cache/3.9/importlib/resources

## Folder: .mypy_cache/3.9/importlib/metadata

## Folder: .mypy_cache/3.9/pydantic

## Folder: .mypy_cache/3.9/pydantic/v1

## Folder: .mypy_cache/3.9/pydantic/_internal

## Folder: .mypy_cache/3.9/pydantic/plugin

## Folder: .mypy_cache/3.9/pydantic/deprecated

## Folder: .mypy_cache/3.9/collections

## Folder: .mypy_cache/3.9/typing_inspection

## Folder: .mypy_cache/3.9/asyncio

## Folder: .mypy_cache/3.9/logging

## Folder: .mypy_cache/3.9/email

## Folder: .mypy_cache/3.9/pydantic_core

## Folder: .mypy_cache/3.9/pandas

## Folder: .mypy_cache/3.9/pandas/core

## Folder: .mypy_cache/3.9/pandas/core/reshape

## Folder: .mypy_cache/3.9/pandas/core/tools

## Folder: .mypy_cache/3.9/pandas/core/util

## Folder: .mypy_cache/3.9/pandas/core/interchange

## Folder: .mypy_cache/3.9/pandas/core/dtypes

## Folder: .mypy_cache/3.9/pandas/core/groupby

## Folder: .mypy_cache/3.9/pandas/core/computation

## Folder: .mypy_cache/3.9/pandas/core/window

## Folder: .mypy_cache/3.9/pandas/core/arrays

## Folder: .mypy_cache/3.9/pandas/core/arrays/arrow

## Folder: .mypy_cache/3.9/pandas/core/arrays/sparse

## Folder: .mypy_cache/3.9/pandas/core/indexes

## Folder: .mypy_cache/3.9/pandas/util

## Folder: .mypy_cache/3.9/pandas/io

## Folder: .mypy_cache/3.9/pandas/io/parsers

## Folder: .mypy_cache/3.9/pandas/io/formats

## Folder: .mypy_cache/3.9/pandas/io/excel

## Folder: .mypy_cache/3.9/pandas/io/json

## Folder: .mypy_cache/3.9/pandas/io/sas

## Folder: .mypy_cache/3.9/pandas/tseries

## Folder: .mypy_cache/3.9/pandas/_testing

## Folder: .mypy_cache/3.9/pandas/_libs

## Folder: .mypy_cache/3.9/pandas/_libs/tslibs

## Folder: .mypy_cache/3.9/pandas/plotting

## Folder: .mypy_cache/3.9/pandas/arrays

## Folder: .mypy_cache/3.9/pandas/api

## Folder: .mypy_cache/3.9/pandas/api/indexers

## Folder: .mypy_cache/3.9/pandas/api/types

## Folder: .mypy_cache/3.9/pandas/api/interchange

## Folder: .mypy_cache/3.9/pandas/api/extensions

## Folder: .mypy_cache/3.9/pandas/api/typing

## Folder: .mypy_cache/3.9/pandas/errors

## Folder: .mypy_cache/3.9/pandas/_config

## Folder: examples

### File: `athena_client/examples/simple_demo.py`
<a name="athena_client-examples-simple_demopy"></a>
```python
#!/usr/bin/env python3
"""
Simple example script demonstrating the athena-client package with mocked responses.
"""
import os
import sys
from unittest.mock import patch

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.models import (
    ConceptClass, ConceptDetails, ConceptType, Domain, Vocabulary
)
from athena_client.query import Q

# Mock response data
MOCK_SEARCH_RESPONSE = {
    "content": [
        {
            "id": 1127433,
            "name": "Aspirin",
            "domain_id": "Drug",
            "vocabulary_id": "RxNorm",
            "concept_class_id": "Ingredient",
            "standard_concept": "S",
            "concept_code": "1191",
            "valid_start_date": "2000-01-01",
            "valid_end_date": "2099-12-31",
            "invalid_reason": None,
            "domain": {"id": 13, "name": "Drug"},
            "vocabulary": {"id": "RxNorm", "name": "RxNorm"},
            "concept_class": {"id": "Ingredient", "name": "Ingredient"}
        }
    ],
    "pageable": {
        "sort": {"sorted": True, "unsorted": False, "empty": False},
        "pageSize": 20,
        "pageNumber": 0,
        "offset": 0,
        "paged": True,
        "unpaged": False
    },
    "totalElements": 1,
    "last": True,
    "totalPages": 1,
    "first": True,
    "sort": {"sorted": True, "unsorted": False, "empty": False},
    "size": 20,
    "number": 0,
    "numberOfElements": 1,
    "empty": False
}

# Create mock ConceptDetails object directly
MOCK_CONCEPT_DETAILS = ConceptDetails(
    id=1127433,
    name="Aspirin",
    domain_id="Drug",
    vocabulary_id="RxNorm",
    concept_class_id="Ingredient",
    standard_concept=ConceptType.STANDARD,
    concept_code="1191",
    valid_start_date="2000-01-01",
    valid_end_date="2099-12-31",
    invalid_reason=None,
    domain=Domain(id=13, name="Drug"),
    vocabulary=Vocabulary(id="RxNorm", name="RxNorm"),
    concept_class=ConceptClass(id="Ingredient", name="Ingredient"),
    synonyms=["Acetylsalicylic Acid", "ASA"],
    additional_information={"atc_codes": ["B01AC06", "N02BA01"]}
)


def main():
    """Demo using the Athena facade with mocked API responses."""
    print("Creating Athena client...")
    
    # Mock the client methods to return test data
    with patch(
        'athena_client.client.AthenaClient.search_concepts',
        return_value=MOCK_SEARCH_RESPONSE
    ), patch(
        'athena_client.client.AthenaClient.get_concept_details',
        return_value=MOCK_CONCEPT_DETAILS
    ):
        athena = Athena()
        
        # Simple text search
        print("\nPerforming simple search for 'aspirin'...")
        results = athena.search("aspirin")
        print(f"Found {results.total} total results, showing top 3:")
        
        for concept in results.top(3):
            print(f"  - [{concept.id}] {concept.name} ({concept.vocabulary.name})")
        
        # Using Query DSL
        print("\nUsing Query DSL to search for 'heart' OR 'cardiac' terms...")
        query = Q.term("heart") | Q.term("cardiac")
        complex_results = athena.search(query)
        print(f"Found {complex_results.total} total results, showing top 3:")
        
        for concept in complex_results.top(3):
            print(f"  - [{concept.id}] {concept.name} ({concept.vocabulary.name})")
        
        # Get concept details
        print("\nGetting details for concept ID 1127433 (Aspirin)...")
        concept_id = 1127433
        details = athena.details(concept_id)
        print(
            f"Concept details: {details.name} - "
            f"{details.concept_class.name} in {details.vocabulary.name}"
        )
        if details.synonyms:
            print(f"Synonyms: {', '.join(details.synonyms)}")
    
    # Capabilities (doesn't need mocking as it's static)
    print("\nListing capabilities:")
    caps = Athena.capabilities()
    for verb, info in caps.items():
        print(f"  - {verb}: {', '.join(info.get('outputs', []))}")


if __name__ == "__main__":
    main()

```

## Folder: .venv

## Folder: .venv/include

## Folder: .venv/include/python3.13

## Folder: .venv/lib

## Folder: .venv/lib/python3.13

## Folder: .venv/share

## Folder: .venv/share/man

## Folder: .venv/share/man/man1

## Folder: .github

## Folder: .github/workflows

### File: `athena_client/.github/workflows/ci.yml`
<a name="athena_client-github-workflows-ciyml"></a>
```yaml
name: CI

on: [push, pull_request]

jobs:
  security:
    name: Security Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Hatch
        run: pip install hatch
      - name: Install dev deps
        run: hatch env create
      - name: Bandit
        run: make bandit

  test:
    name: Tests & SBOM
    needs: security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install Hatch
        run: pip install hatch
      - name: Install dev deps
        run: hatch env create
      - name: Test suite
        run: hatch run cov
      - name: Generate SBOM
        if: github.ref == 'refs/heads/main'
        run: make cyclonedx
      - name: Upload SBOM
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json

```

## Folder: build

## Folder: build/bdist.macosx-15.0-arm64

## Folder: build/lib

## Folder: build/lib/athena_client

### File: `athena_client/build/lib/athena_client/__init__.py`
<a name="athena_client-build-lib-athena_client-__init__py"></a>
```python
"""
athena-client: Production-ready Python SDK for the OHDSI Athena Concepts API
"""
from typing import Any, Dict, Optional

from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship


__version__ = "1.0.0"


class Athena:
    """
    Main facade for the Athena API client.
    
    This class provides a simplified interface to the Athena API with six
    intuitive verbs that cover 95% of day-to-day use cases.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the Athena facade with optional configuration.
        
        Args:
            base_url: The base URL for the Athena API.
            token: Bearer token for authentication.
            client_id: Client ID for HMAC authentication.
            private_key: Private key for HMAC signing.
            timeout: HTTP timeout in seconds.
            max_retries: Maximum number of retry attempts.
            backoff_factor: Exponential backoff factor for retries.
        """
        # Import here to avoid circular imports
        from .client import AthenaClient  # pylint: disable=import-outside-toplevel
        
        self._client = AthenaClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
    
    def search(
        self,
        query: Any,  # Can be str or Q object
        *,
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> "SearchResult":
        """
        Search for concepts in the Athena vocabulary.
        
        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status
            
        Returns:
            SearchResult object containing the search results
        """
        from .search_result import SearchResult
        
        # Handle Q object if provided
        query_str = query
        if hasattr(query, "to_boosts") and callable(query.to_boosts):
            boosts = query.to_boosts()
            query_str = ""
            
        data = self._client.search_concepts(
            query=query_str,
            exact=exact,
            fuzzy=fuzzy,
            wildcard=wildcard,
            boosts=boosts,
            debug=debug,
            page_size=page_size,
            page=page,
            domain=domain,
            vocabulary=vocabulary,
            standard_concept=standard_concept,
        )
        
        return SearchResult(data)
    
    def details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.
        
        Args:
            concept_id: The concept ID to get details for
            
        Returns:
            ConceptDetails object
        """
        return self._client.get_concept_details(concept_id)
    
    def relationships(
        self,
        concept_id: int,
        *,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.
        
        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts
            
        Returns:
            ConceptRelationship object
        """
        return self._client.get_concept_relationships(
            concept_id=concept_id,
            relationship_id=relationship_id,
            only_standard=only_standard,
        )
    
    def graph(
        self,
        concept_id: int,
        *,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.
        
        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph
            
        Returns:
            ConceptRelationsGraph object
        """
        return self._client.get_concept_graph(
            concept_id=concept_id,
            depth=depth,
            zoom_level=zoom_level,
        )
    
    def summary(self, concept_id: int) -> Dict[str, Any]:
        """
        Get a comprehensive summary for a concept.
        
        This aggregates details, relationships, and graph information.
        
        Args:
            concept_id: The concept ID to summarize
            
        Returns:
            Dictionary containing details, relationships, and graph
        """
        details = self.details(concept_id)
        relationships = self.relationships(concept_id)
        graph = self.graph(concept_id)
        
        return {
            "details": details,
            "relationships": relationships,
            "graph": graph,
        }
    
    @staticmethod
    def capabilities() -> Dict[str, Dict[str, Any]]:
        """
        Get machine-readable manifest of all supported verbs.
        
        Returns:
            Dictionary containing capabilities information
        """
        return {
            "search": {
                "endpoint": "/concepts",
                "auth": "anonymous|bearer",
                "outputs": ["models", "list", "dataframe", "json", "yaml", "csv"]
            },
            "details": {
                "endpoint": "/concepts/{id}",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"]
            },
            "relationships": {
                "endpoint": "/concepts/{id}/relationships",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"]
            },
            "graph": {
                "endpoint": "/concepts/{id}/relations",
                "auth": "anonymous|bearer",
                "outputs": ["model", "json"]
            },
            "summary": {
                "composed_of": ["details", "relationships", "graph"],
                "outputs": ["dict"]
            }
        }

# Type hint for return annotation - needed at the end to avoid circular imports
# This import is used for type hints only, which is why it's placed at the bottom
from .search_result import SearchResult  # noqa: E402

```

### File: `athena_client/build/lib/athena_client/async_client.py`
<a name="athena_client-build-lib-athena_client-async_clientpy"></a>
```python
"""
Asynchronous Athena API client implementation.

This module provides an asynchronous client for the Athena API using httpx.
"""
import json
import logging
from typing import Any, Dict, Optional, Union, cast
from urllib.parse import urljoin

import backoff

try:
    import httpx
except ImportError as err:
    raise ImportError(
        "httpx is required for the async client. "
        "Install with 'pip install \"athena-client[async]\"'"
    ) from err

from .auth import build_headers
from .exceptions import AthenaError, ClientError, NetworkError, ServerError
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship
from .settings import get_settings

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """
    Asynchronous HTTP client for making requests to the Athena API.
    
    Features:
    - Automatic retry with exponential backoff
    - Custom timeout handling
    - Authentication header generation
    - Error handling and mapping to typed exceptions
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the async HTTP client with configuration.
        
        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        settings = get_settings()
        
        # Use provided values or fall back to settings
        self.base_url = base_url or settings.ATHENA_BASE_URL
        
        # Set up token and HMAC if provided
        if token is not None:
            settings.ATHENA_TOKEN = token
        if client_id is not None:
            settings.ATHENA_CLIENT_ID = client_id
        if private_key is not None:
            settings.ATHENA_PRIVATE_KEY = private_key
            
        self.timeout = timeout or settings.ATHENA_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.ATHENA_MAX_RETRIES
        self.backoff_factor = backoff_factor or settings.ATHENA_BACKOFF_FACTOR
        
        # Create httpx client
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.
        
        Args:
            path: API endpoint path
            
        Returns:
            Full URL
        """
        return urljoin(self.base_url, path)
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: HTTP response from httpx
            
        Returns:
            Parsed JSON response
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            else:
                raise
        except httpx.DecodingError as e:
            raise AthenaError(f"Invalid JSON response: {e}") from e
    
    @backoff.on_exception(
        backoff.expo,
        (httpx.TimeoutException, httpx.ConnectError),
        max_tries=3,
        factor=0.3,
    )
    async def request(
        self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None, raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make an HTTP request to the Athena API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        url = self._build_url(path)
        body_bytes = b""
        
        # Convert data to JSON bytes if provided
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")
            
        # Build authentication headers
        headers = build_headers(method, url, body_bytes)
        
        # Add Content-Type header if sending data
        if data is not None:
            headers["Content-Type"] = "application/json"
        
        # Generate a correlation ID for logging
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(f"[{correlation_id}] {method} {url}")
            
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                content=body_bytes if data is not None else None,
                headers=headers,
                timeout=self.timeout,
            )
            
            logger.debug(
                f"[{correlation_id}] {response.status_code} {response.reason_phrase}"
            )
                
            if raw_response:
                return response
                
            return await self._handle_response(response)
            
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            logger.warning(f"[{correlation_id}] Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e
        
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make a GET request to the Athena API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
        """
        return await self.request("GET", path, params=params, raw_response=raw_response)
    
    async def post(
        self,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], httpx.Response]:
        """
        Make a POST request to the Athena API.
        
        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
        """
        return await self.request(
            "POST", path, data=data, params=params, raw_response=raw_response
        )


class AthenaAsyncClient:
    """
    Asynchronous client for the Athena API.
    
    This class provides asynchronous access to all Athena API endpoints
    with minimal abstraction, returning parsed Pydantic models.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the async Athena client with configuration.
        
        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.http = AsyncHttpClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
    
    async def search_concepts(
        self,
        query: str = "",
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for concepts in the Athena vocabulary.
        
        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status
            
        Returns:
            Raw API response data
        """
        params: Dict[str, Any] = {"pageSize": page_size, "page": page}
        
        # Add query if provided
        if query:
            params["query"] = query
        
        # Add filters if provided
        if exact:
            params["exact"] = exact
        if fuzzy:
            params["fuzzy"] = str(fuzzy).lower()
        if wildcard:
            params["wildcard"] = wildcard
        if domain:
            params["domain"] = domain
        if vocabulary:
            params["vocabulary"] = vocabulary
        if standard_concept:
            params["standardConcept"] = standard_concept
            
        # If boosts provided, use debug endpoint and include boosts in request
        if boosts or debug:
            response = await self.http.post(
                "/concepts",
                data={"boosts": boosts} if boosts else {},
                params=params,
            )
            return cast(Dict[str, Any], response)
        
        # Otherwise use standard GET endpoint
        response = await self.http.get("/concepts", params=params)
        return cast(Dict[str, Any], response)
    
    async def get_concept_details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.
        
        Args:
            concept_id: The concept ID to get details for
            
        Returns:
            ConceptDetails object
        """
        response = await self.http.get(f"/concepts/{concept_id}")
        data = cast(Dict[str, Any], response)
        return ConceptDetails.model_validate(data)
    
    async def get_concept_relationships(
        self,
        concept_id: int,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.
        
        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts
            
        Returns:
            ConceptRelationship object
        """
        params: Dict[str, Any] = {}
        
        if relationship_id:
            params["relationshipId"] = relationship_id
        if only_standard:
            params["standardConcepts"] = "true"
            
        response = await self.http.get(
            f"/concepts/{concept_id}/relationships", params=params
        )
        data = cast(Dict[str, Any], response)
        return ConceptRelationship.model_validate(data)
    
    async def get_concept_graph(
        self,
        concept_id: int,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.
        
        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph
            
        Returns:
            ConceptRelationsGraph object
        """
        params = {"depth": depth, "zoomLevel": zoom_level}
        response = await self.http.get(
            f"/concepts/{concept_id}/relations", params=params
        )
        data = cast(Dict[str, Any], response)
        return ConceptRelationsGraph.model_validate(data)

```

### File: `athena_client/build/lib/athena_client/auth.py`
<a name="athena_client-build-lib-athena_client-authpy"></a>
```python
"""
Authentication module for the Athena client.

This module handles Bearer token and HMAC authentication for the Athena API.
"""
from typing import Any, Dict

from .settings import get_settings


def build_headers(method: str, url: str, body: bytes) -> Dict[str, str]:
    """
    Build authentication headers for Athena API requests.
    
    If a token is supplied, adds Bearer authentication.
    If a private key is supplied, adds HMAC signature.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full request URL
        body: Request body as bytes
    
    Returns:
        Dictionary of headers to add to the request
    """
    s = get_settings()
    if s.ATHENA_TOKEN is None:
        return {}
        
    hdrs = {
        "X-Athena-Auth": f"Bearer {s.ATHENA_TOKEN}",
        "X-Athena-Client-Id": s.ATHENA_CLIENT_ID or "athena-client",
    }
    
    if s.ATHENA_PRIVATE_KEY:  
        # Import here for optional dependency
        try:
            from base64 import b64encode
            from datetime import datetime
            from cryptography.hazmat.primitives import hashes, serialization
            
            nonce = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            to_sign = f"{method}\n{url}\n\n{nonce}\n{body.decode()}"
            key = serialization.load_pem_private_key(
                s.ATHENA_PRIVATE_KEY.encode(), password=None
            )
            signing_key: Any = key
            sig = signing_key.sign(to_sign.encode(), hashes.SHA256())
            hdrs.update({
                "X-Athena-Nonce": nonce,
                "X-Athena-Hmac": b64encode(sig).decode()
            })
        except ImportError:
            import logging
            logging.warning(
                "cryptography package is required for HMAC signing. "
                "Install with 'pip install \"athena-client[crypto]\"'"
            )
            
    return hdrs

```

### File: `athena_client/build/lib/athena_client/cli.py`
<a name="athena_client-build-lib-athena_client-clipy"></a>
```python
"""
Command-line interface for the Athena client.

This module provides a CLI for interacting with the Athena API.
"""
import json
import sys
from typing import Any, Optional

try:
    import click
except ImportError:
    click = None  # type: ignore
    print(
        "The 'click' package is required for the CLI. "
        "Install with 'pip install \"athena-client[cli]\"'"
    )
    sys.exit(1)

try:
    import rich
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
except ImportError:
    rich = None  # type: ignore
    Console = None  # type: ignore
    Syntax = None  # type: ignore
    Table = None  # type: ignore

from . import Athena, __version__


def _create_client(
    base_url: Optional[str],
    token: Optional[str],
    timeout: Optional[int],
    retries: Optional[int],
) -> Athena:
    """
    Create an Athena client with the given parameters.
    
    Args:
        base_url: Base URL for the Athena API
        token: Bearer token for authentication
        timeout: HTTP timeout in seconds
        retries: Maximum number of retry attempts
        
    Returns:
        Athena client
    """
    return Athena(
        base_url=base_url,
        token=token,
        timeout=timeout,
        max_retries=retries,
    )


def _format_output(
    data: object,
    output: str,
    console: Optional[Console] = None
) -> None:
    """
    Format and print data based on the requested output format.
    
    Args:
        data: Data to format and print
        output: Output format (json, yaml, table, pretty)
        console: Rich console for pretty printing
    """
    if output == "json":
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))
    elif output == "yaml":
        try:
            import yaml
        except ImportError:
            print(
                "The 'pyyaml' package is required for YAML output. "
                "Install with 'pip install \"athena-client[yaml]\"'"
            )
            sys.exit(1)
            
        print(yaml.dump(data))
    elif output == "table" and console is not None and rich is not None:
        if hasattr(data, "to_list"):
            # Handle SearchResult
            results = data.to_list()
            if not results:
                console.print("[yellow]No results found[/yellow]")
                return
                
            table = Table(title="Athena Concepts")
            
            # Add columns
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Code", style="magenta")
            table.add_column("Vocabulary", style="blue")
            table.add_column("Domain", style="yellow")
            table.add_column("Class", style="red")
            
            # Add rows
            for item in results:
                table.add_row(
                    str(item["id"]),
                    item["name"],
                    item["concept_code"],
                    item["vocabulary"]["name"],
                    item["domain"]["name"],
                    item["concept_class"]["name"],
                )
                
            console.print(table)
        else:
            # Just pretty-print JSON for other data types
            syntax = Syntax(
                json.dumps(data, indent=2, default=str),
                "json",
                theme="monokai",
                word_wrap=True,
            )
            console.print(syntax)
    elif output == "pretty" and console is not None and rich is not None:
        # Use rich's pretty printing
        console.print(data)
    else:
        # Fall back to regular JSON
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))


@click.group()
@click.version_option(__version__)
@click.option(
    "--base-url",
    envvar="ATHENA_BASE_URL",
    help="Base URL for the Athena API",
)
@click.option(
    "--token",
    envvar="ATHENA_TOKEN",
    help="Bearer token for authentication",
)
@click.option(
    "--timeout",
    type=int,
    envvar="ATHENA_TIMEOUT_SECONDS",
    help="HTTP timeout in seconds",
)
@click.option(
    "--retries",
    type=int,
    envvar="ATHENA_MAX_RETRIES",
    help="Maximum number of retry attempts",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["json", "yaml", "table", "pretty"]),
    default="table",
    help="Output format",
)
@click.pass_context
def cli(
    ctx: click.Context,
    base_url: Optional[str],
    token: Optional[str],
    timeout: Optional[int],
    retries: Optional[int],
    output: str,
) -> None:
    """Athena Client CLI - Interact with the OHDSI Athena API."""
    ctx.ensure_object(dict)
    ctx.obj["base_url"] = base_url
    ctx.obj["token"] = token
    ctx.obj["timeout"] = timeout
    ctx.obj["retries"] = retries
    ctx.obj["output"] = output
    
    # Set up rich console if available
    if rich is not None:
        ctx.obj["console"] = Console()
    else:
        ctx.obj["console"] = None


@cli.command()
@click.argument("query")
@click.option("--fuzzy/--no-fuzzy", default=False, help="Enable fuzzy matching")
@click.option("--page-size", type=int, default=20, help="Number of results per page")
@click.option("--page", type=int, default=0, help="Page number (0-indexed)")
@click.option("--domain", help="Filter by domain")
@click.option("--vocabulary", help="Filter by vocabulary")
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    fuzzy: bool,
    page_size: int,
    page: int,
    domain: Optional[str],
    vocabulary: Optional[str],
) -> None:
    """Search for concepts in the Athena vocabulary."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    results = client.search(
        query,
        fuzzy=fuzzy,
        page_size=page_size,
        page=page,
        domain=domain,
        vocabulary=vocabulary,
    )
    
    # Get the appropriate output based on the format
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = results.to_json()
    elif ctx.obj["output"] == "yaml":
        output_data = results.to_yaml()
    else:
        output_data = results
        
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.pass_context
def details(ctx: click.Context, concept_id: int) -> None:
    """Get detailed information for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.details(concept_id)
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.option("--relationship-id", help="Filter by relationship type")
@click.option(
    "--only-standard/--all",
    default=False,
    help="Only include standard concepts"
)
@click.pass_context
def relationships(
    ctx: click.Context,
    concept_id: int,
    relationship_id: Optional[str],
    only_standard: bool
) -> None:
    """Get relationships for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.relationships(
        concept_id,
        relationship_id=relationship_id,
        only_standard=only_standard,
    )
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.option("--depth", type=int, default=10, help="Maximum depth of relationships")
@click.option("--zoom-level", type=int, default=4, help="Zoom level for the graph")
@click.pass_context
def graph(
    ctx: click.Context, concept_id: int, depth: int, zoom_level: int
) -> None:
    """Get relationship graph for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.graph(
        concept_id,
        depth=depth,
        zoom_level=zoom_level,
    )
    output_data: Any
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.pass_context
def summary(ctx: click.Context, concept_id: int) -> None:
    """Get a comprehensive summary for a concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.summary(concept_id)
    
    # Convert Pydantic models to dicts for serialization
    output_data = {
        "details": result["details"].model_dump(),
        "relationships": result["relationships"].model_dump(),
        "graph": result["graph"].model_dump(),
    }
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command(name="caps")
@click.pass_context
def capabilities(ctx: click.Context) -> None:
    """List capabilities of the Athena client."""
    caps = Athena.capabilities()
    _format_output(caps, ctx.obj["output"], ctx.obj.get("console"))


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})  # pylint: disable=unexpected-keyword-arg


if __name__ == "__main__":
    main()

```

### File: `athena_client/build/lib/athena_client/client.py`
<a name="athena_client-build-lib-athena_client-clientpy"></a>
```python
"""
Athena API client implementation.

This module provides the core synchronous client for the Athena API.
"""
from typing import Any, Dict, Optional, cast

from .http import HttpClient
from .models import ConceptDetails, ConceptRelationsGraph, ConceptRelationship


class AthenaClient:
    """
    Core synchronous client for the Athena API.
    
    This class provides direct access to all Athena API endpoints
    with minimal abstraction, returning parsed Pydantic models.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the Athena client with configuration.
        
        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        self.http = HttpClient(
            base_url=base_url,
            token=token,
            client_id=client_id,
            private_key=private_key,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )
    
    def search_concepts(
        self,
        query: str = "",
        exact: Optional[str] = None,
        fuzzy: bool = False,
        wildcard: Optional[str] = None,
        boosts: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        page_size: int = 20,
        page: int = 0,
        domain: Optional[str] = None,
        vocabulary: Optional[str] = None,
        standard_concept: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for concepts in the Athena vocabulary.
        
        Args:
            query: The search query string
            exact: Exact match phrase
            fuzzy: Whether to enable fuzzy matching
            wildcard: Wildcard pattern
            boosts: Dictionary of field boosts
            debug: Enable debug mode
            page_size: Number of results per page
            page: Page number (0-indexed)
            domain: Filter by domain
            vocabulary: Filter by vocabulary
            standard_concept: Filter by standard concept status
            
        Returns:
            Raw API response data
        """
        params: Dict[str, Any] = {"pageSize": page_size, "page": page}
        
        # Add query if provided
        if query:
            params["query"] = query
        
        # Add filters if provided
        if exact:
            params["exact"] = exact
        if fuzzy:
            params["fuzzy"] = str(fuzzy).lower()
        if wildcard:
            params["wildcard"] = wildcard
        if domain:
            params["domain"] = domain
        if vocabulary:
            params["vocabulary"] = vocabulary
        if standard_concept:
            params["standardConcept"] = standard_concept
            
        # If boosts provided, use debug endpoint and include boosts in request
        if boosts or debug:
            return cast(Dict[str, Any], self.http.post(
                "/concepts",
                data={"boosts": boosts} if boosts else {},
                params=params,
            ))
        
        # Otherwise use standard GET endpoint
        return cast(Dict[str, Any], self.http.get("/concepts", params=params))
    
    def get_concept_details(self, concept_id: int) -> ConceptDetails:
        """
        Get detailed information for a specific concept.
        
        Args:
            concept_id: The concept ID to get details for
            
        Returns:
            ConceptDetails object
        """
        data = self.http.get(f"/concepts/{concept_id}")
        return ConceptDetails.model_validate(data)
    
    def get_concept_relationships(
        self,
        concept_id: int,
        relationship_id: Optional[str] = None,
        only_standard: bool = False,
    ) -> ConceptRelationship:
        """
        Get relationships for a specific concept.
        
        Args:
            concept_id: The concept ID to get relationships for
            relationship_id: Filter by relationship type
            only_standard: Only include standard concepts
            
        Returns:
            ConceptRelationship object
        """
        params: Dict[str, Any] = {}
        
        if relationship_id:
            params["relationshipId"] = relationship_id
        if only_standard:
            params["standardConcepts"] = "true"
            
        data = self.http.get(f"/concepts/{concept_id}/relationships", params=params)
        return ConceptRelationship.model_validate(data)
    
    def get_concept_graph(
        self,
        concept_id: int,
        depth: int = 10,
        zoom_level: int = 4,
    ) -> ConceptRelationsGraph:
        """
        Get relationship graph for a specific concept.
        
        Args:
            concept_id: The concept ID to get graph for
            depth: Maximum depth of relationships to traverse
            zoom_level: Zoom level for the graph
            
        Returns:
            ConceptRelationsGraph object
        """
        params = {"depth": depth, "zoomLevel": zoom_level}
        data = self.http.get(f"/concepts/{concept_id}/relations", params=params)
        return ConceptRelationsGraph.model_validate(data)

```

### File: `athena_client/build/lib/athena_client/exceptions.py`
<a name="athena_client-build-lib-athena_client-exceptionspy"></a>
```python
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

```

### File: `athena_client/build/lib/athena_client/http.py`
<a name="athena_client-build-lib-athena_client-httppy"></a>
```python
"""
HTTP client implementation for Athena API.

This module provides HTTP clients for making requests to the Athena API,
with features like retry, backoff, and timeout handling.
"""
import json
import logging
from typing import Any, Dict, Optional, TypeVar, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import build_headers
from .exceptions import AthenaError, ClientError, NetworkError, ServerError
from .settings import get_settings

# Type variable for generic response
T = TypeVar("T")

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Synchronous HTTP client for making requests to the Athena API.
    
    Features:
    - Automatic retry with exponential backoff
    - Custom timeout handling
    - Authentication header generation
    - Error handling and mapping to typed exceptions
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        private_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
    ) -> None:
        """
        Initialize the HTTP client with configuration.
        
        Args:
            base_url: Base URL for the Athena API
            token: Bearer token for authentication
            client_id: Client ID for HMAC authentication
            private_key: Private key for HMAC signing
            timeout: HTTP timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor for retries
        """
        settings = get_settings()
        
        # Use provided values or fall back to settings
        self.base_url = base_url or settings.ATHENA_BASE_URL
        
        # Set up token and HMAC if provided
        if token is not None:
            settings.ATHENA_TOKEN = token
        if client_id is not None:
            settings.ATHENA_CLIENT_ID = client_id
        if private_key is not None:
            settings.ATHENA_PRIVATE_KEY = private_key
            
        self.timeout = timeout or settings.ATHENA_TIMEOUT_SECONDS
        self.max_retries = max_retries or settings.ATHENA_MAX_RETRIES
        self.backoff_factor = backoff_factor or settings.ATHENA_BACKOFF_FACTOR
        
        # Create session with retry configuration
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """
        Create and configure a requests Session with retry logic.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _build_url(self, path: str) -> str:
        """
        Build full URL by joining base URL and path.
        
        Args:
            path: API endpoint path
            
        Returns:
            Full URL
        """
        return urljoin(self.base_url, path)
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.
        
        Args:
            response: HTTP response from requests
            
        Returns:
            Parsed JSON response
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if 400 <= response.status_code < 500:
                raise ClientError(
                    f"Client error: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            elif response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code} {response.reason}",
                    status_code=response.status_code,
                    response=response.text,
                ) from e
            else:
                raise
        except requests.exceptions.JSONDecodeError as e:
            raise AthenaError(f"Invalid JSON response: {e}") from e
    
    def request(
        self,
        method: str,
        path: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False,
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make an HTTP request to the Athena API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            data: Request body data
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
            
        Raises:
            ClientError: For 4xx status codes
            ServerError: For 5xx status codes
            NetworkError: For connection errors
        """
        url = self._build_url(path)
        body_bytes = b""
        
        # Convert data to JSON bytes if provided
        if data is not None:
            body_bytes = json.dumps(data).encode("utf-8")
            
        # Build authentication headers
        headers = build_headers(method, url, body_bytes)
        
        # Add Content-Type header if sending data
        if data is not None:
            headers["Content-Type"] = "application/json"
        
        # Generate a correlation ID for logging
        correlation_id = f"req-{id(self)}-{id(path)}"
        logger.debug(f"[{correlation_id}] {method} {url}")
            
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=body_bytes if data is not None else None,
                headers=headers,
                timeout=self.timeout,
            )
            
            logger.debug(
                f"[{correlation_id}] {response.status_code} {response.reason}"
            )
                
            if raw_response:
                return response
                
            return self._handle_response(response)
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logger.warning(f"[{correlation_id}] Network error: {e}")
            raise NetworkError(f"Network error: {e}") from e
    
    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a GET request to the Athena API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
        """
        return self.request("GET", path, params=params, raw_response=raw_response)
    
    def post(
        self, path: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None,
        raw_response: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make a POST request to the Athena API.
        
        Args:
            path: API endpoint path
            data: Request body data
            params: Query parameters
            raw_response: Whether to return the raw response object
            
        Returns:
            Parsed JSON response or raw Response object
        """
        return self.request("POST", path, data=data, params=params, raw_response=raw_response)

```

### File: `athena_client/build/lib/athena_client/query.py`
<a name="athena_client-build-lib-athena_client-querypy"></a>
```python
"""
Query DSL for building complex Athena queries.

This module provides a Query DSL that allows for building complex queries
using a fluent interface and operator overloading.
"""
from typing import Any, Dict, Optional


class Q:
    """
    Query DSL for building complex Athena queries.
    
    Usage:
        q = Q.term("diabetes")
        q = Q.phrase("heart attack")
        q = Q.exact('"Myocardial Infarction"')
        q = Q.wildcard("aspir*")
        
        # Combine with operators
        q = Q.term("diabetes") & Q.term("type 2")  # AND
        q = Q.term("heart") | Q.term("cardiac")    # OR
        q = -Q.term("chronic")                     # NOT
        
        # Apply modifiers
        q = Q.term("aspirin").fuzzy(0.8)
        
        # Get boosts for the API
        boosts = q.to_boosts()
    """
    
    def __init__(self, query_type: str, value: str, **kwargs: Any) -> None:
        """
        Initialize a query object.
        
        Args:
            query_type: Type of query (term, phrase, exact, wildcard)
            value: Query value
            **kwargs: Additional options
        """
        self.query_type = query_type
        self.value = value
        self.options = kwargs
        self.operator: Optional[str] = None
        self.left: Optional["Q"] = None
        self.right: Optional["Q"] = None
    
    @classmethod
    def term(cls, value: str) -> "Q":
        """
        Create a term query.
        
        Args:
            value: Term to search for
        
        Returns:
            Query object
        """
        return cls("term", value)
    
    @classmethod
    def phrase(cls, value: str) -> "Q":
        """
        Create a phrase query.
        
        Args:
            value: Phrase to search for
        
        Returns:
            Query object
        """
        return cls("phrase", value)
    
    @classmethod
    def exact(cls, value: str) -> "Q":
        """
        Create an exact match query.
        
        Args:
            value: Exact phrase to search for (should be in quotes)
        
        Returns:
            Query object
        """
        if not value.startswith('"') or not value.endswith('"'):
            value = f'"{value}"'
        return cls("exact", value)
    
    @classmethod
    def wildcard(cls, value: str) -> "Q":
        """
        Create a wildcard query.
        
        Args:
            value: Wildcard pattern (e.g., "aspir*")
        
        Returns:
            Query object
        """
        if not value.endswith("*"):
            value = f"{value}*"
        return cls("wildcard", value)
    
    def fuzzy(self, ratio: float = 0.7) -> "Q":
        """
        Apply fuzzy matching to the query.
        
        Args:
            ratio: Fuzzy match ratio (0.0 - 1.0)
        
        Returns:
            Query object with fuzzy matching
        """
        self.options["fuzzy"] = ratio
        return self
    
    def __and__(self, other: "Q") -> "Q":
        """
        Combine with AND operator.
        
        Args:
            other: Another Q object
        
        Returns:
            New Q object representing the AND condition
        """
        result = Q("compound", "")
        result.operator = "AND"
        result.left = self
        result.right = other
        return result
    
    def __or__(self, other: "Q") -> "Q":
        """
        Combine with OR operator.
        
        Args:
            other: Another Q object
        
        Returns:
            New Q object representing the OR condition
        """
        result = Q("compound", "")
        result.operator = "OR"
        result.left = self
        result.right = other
        return result
    
    def __neg__(self) -> "Q":
        """
        Apply NOT operator.
        
        Returns:
            New Q object representing the NOT condition
        """
        result = Q("compound", "")
        result.operator = "NOT"
        result.right = self
        return result
    
    def to_boosts(self) -> Dict[str, Any]:
        """
        Convert the query to a boosts dictionary for the Athena API.
        
        Returns:
            Dictionary with query boosts
        """
        if self.query_type == "compound":
            if self.operator == "AND":
                assert self.left is not None and self.right is not None
                boosts_left = self.left.to_boosts()
                boosts_right = self.right.to_boosts()
                # Merge the boosts with AND logic
                return {
                    "filter": {
                        "bool": {
                            "must": [
                                boosts_left.get("filter", {}),
                                boosts_right.get("filter", {})
                            ]
                        }
                    }
                }
            elif self.operator == "OR":
                assert self.left is not None and self.right is not None
                boosts_left = self.left.to_boosts()
                boosts_right = self.right.to_boosts()
                # Merge the boosts with OR logic
                return {
                    "filter": {
                        "bool": {
                            "should": [
                                boosts_left.get("filter", {}),
                                boosts_right.get("filter", {})
                            ]
                        }
                    }
                }
            elif self.operator == "NOT":
                assert self.right is not None
                boosts_right = self.right.to_boosts()
                # Apply NOT logic
                return {
                    "filter": {
                        "bool": {
                            "must_not": [boosts_right.get("filter", {})]
                        }
                    }
                }
            
        # Handle basic query types
        query_dict: Dict[str, Any] = {}
        
        if self.query_type == "term":
            query_dict["query"] = self.value
            query_dict["fields"] = [
                "name^10", "synonyms^5", "definition^3", "concept_code"
            ]
        elif self.query_type == "phrase":
            query_dict["query"] = f'"{self.value}"'
            query_dict["fields"] = ["name^10", "synonyms^5", "definition^3"]
        elif self.query_type == "exact":
            query_dict["query"] = self.value
            query_dict["fields"] = ["concept_code^20", "name.exact^15"]
        elif self.query_type == "wildcard":
            query_dict["query"] = self.value
            query_dict["fields"] = ["name^10", "synonyms^5"]
            
        # Apply fuzzy if requested
        if "fuzzy" in self.options:
            query_dict["fuzziness"] = self.options["fuzzy"]
            
        return {"filter": {"query_string": query_dict}}

```

### File: `athena_client/build/lib/athena_client/search_result.py`
<a name="athena_client-build-lib-athena_client-search_resultpy"></a>
```python
"""
SearchResult formatter for Athena search results.

This module provides a class for handling and formatting search results
from the Athena API into various output formats.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Union

from .exceptions import ValidationError
from .models import Concept, ConceptSearchResponse

# Optional imports
pd = None
yaml = None


class SearchResult:
    """
    Formatter for search results from the Athena API.
    
    This class provides methods to convert search results into various formats:
    - Pydantic models (all, top)
    - Python dictionaries (to_list)
    - pandas DataFrames (to_df)
    - JSON (to_json)
    - YAML (to_yaml)
    - CSV (to_csv)
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize with API response data.
        
        Args:
            data: Raw API response from search endpoint
            
        Raises:
            ValidationError: If the data cannot be parsed
        """
        try:
            self._response = ConceptSearchResponse.model_validate(data)
        except Exception as e:
            raise ValidationError(f"Failed to parse search results: {e}") from e
    
    def all(self) -> List[Concept]:
        """
        Get all concepts as Pydantic objects.
        
        Returns:
            List of Concept objects
        """
        return self._response.content
    
    def top(self, n: int = 10) -> List[Concept]:
        """
        Get top N concepts as Pydantic objects.
        
        Args:
            n: Number of concepts to return
            
        Returns:
            List of top N Concept objects
        """
        return self._response.content[:n]
    
    def to_models(self) -> List[Concept]:
        """
        Alias for all().
        
        Returns:
            List of Concept objects
        """
        return self.all()
    
    def to_list(self) -> List[Dict[str, Any]]:
        """
        Get concepts as list of dictionaries.
        
        Returns:
            List of concept dictionaries
        """
        return [concept.model_dump() for concept in self.all()]
    
    def to_df(self) -> Any:
        """
        Get concepts as pandas DataFrame.
        
        Returns:
            pandas DataFrame
            
        Raises:
            ImportError: If pandas is not installed
        """
        global pd
        if pd is None:
            try:
                import pandas as pd_mod
                pd = pd_mod
            except ImportError as err:
                raise ImportError(
                    "pandas is required for DataFrame output. "
                    "Install with 'pip install \"athena-client[pandas]\"'"
                ) from err
        
        return pd.DataFrame(self.to_list())
    
    def to_json(self, indent: int = 2) -> str:
        """
        Get concepts as JSON string.
        
        Args:
            indent: Indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(self.to_list(), indent=indent)
    
    def to_yaml(self) -> str:
        """
        Get concepts as YAML string.
        
        Returns:
            YAML string
            
        Raises:
            ImportError: If PyYAML is not installed
        """
        global yaml
        if yaml is None:
            try:
                import yaml as yaml_mod
                yaml = yaml_mod
            except ImportError as err:
                raise ImportError(
                    "PyYAML is required for YAML output. "
                    "Install with 'pip install \"athena-client[yaml]\"'"
                ) from err
            
        return yaml.dump(self.to_list())
    
    def to_csv(self, path: Union[str, Path]) -> None:
        """
        Write concepts to CSV file.
        
        Args:
            path: File path to write CSV to
            
        Raises:
            ImportError: If pandas is not installed
        """
        df = self.to_df()  # This will raise ImportError if pandas is missing
        df.to_csv(path, index=False)
    
    def __len__(self) -> int:
        """
        Get the number of results.
        
        Returns:
            Number of concepts
        """
        return len(self._response.content)
    
    def __getitem__(self, idx: int) -> Concept:
        """
        Get a specific concept by index.
        
        Args:
            idx: Index of the concept
            
        Returns:
            Concept at the given index
        """
        return self._response.content[idx]
    
    @property
    def total(self) -> int:
        """
        Get the total number of results.
        
        Returns:
            Total number of results
        """
        return self._response.total_elements
    
    @property
    def page(self) -> int:
        """
        Get the current page number.
        
        Returns:
            Current page number
        """
        return self._response.number
    
    @property
    def pages(self) -> int:
        """
        Get the total number of pages.
        
        Returns:
            Total number of pages
        """
        return self._response.total_pages

```

### File: `athena_client/build/lib/athena_client/settings.py`
<a name="athena_client-build-lib-athena_client-settingspy"></a>
```python
"""
Settings module for the Athena client.

This module provides configuration settings loaded from environment variables
or .env files using pydantic-settings.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    """
    Configuration settings for the Athena client.
    
    Settings can be provided via environment variables, .env file, or defaults.
    """
    
    ATHENA_BASE_URL: str = "https://athena.ohdsi.org/api/v1"
    ATHENA_TOKEN: Optional[str] = None
    ATHENA_CLIENT_ID: Optional[str] = None
    ATHENA_PRIVATE_KEY: Optional[str] = None
    ATHENA_TIMEOUT_SECONDS: int = 10
    ATHENA_MAX_RETRIES: int = 3
    ATHENA_BACKOFF_FACTOR: float = 0.3
    
    model_config = SettingsConfigDict(env_file=".env", env_prefix="")


@lru_cache
def get_settings() -> _Settings:
    """
    Get the settings singleton.
    
    Returns:
        Cached instance of _Settings.
    """
    return _Settings()  # cached singleton

```

## Folder: build/lib/athena_client/utils

### File: `athena_client/build/lib/athena_client/utils/__init__.py`
<a name="athena_client-build-lib-athena_client-utils-__init__py"></a>
```python
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

```

## Folder: build/lib/athena_client/models

### File: `athena_client/build/lib/athena_client/models/__init__.py`
<a name="athena_client-build-lib-athena_client-models-__init__py"></a>
```python
"""
Pydantic models for Athena API responses.

This module defines Pydantic models for the various responses from the Athena API.
"""
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, cast

import orjson
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


def _json_dumps(value: Any, *, default: Any) -> str:
    """Serialize to JSON using orjson."""
    return orjson.dumps(value, default=default).decode()


class BaseModel(PydanticBaseModel):
    """Project-wide Pydantic base model using orjson."""

    model_config: ClassVar[ConfigDict] = cast(
        ConfigDict,
        {
            "populate_by_name": True,
            "extra": "ignore",
            "json_loads": orjson.loads,
            "json_dumps": _json_dumps,
        },
    )


class Domain(BaseModel):
    """Domain information for a concept."""
    
    id: int = Field(..., description="Domain ID")
    name: str = Field(..., description="Domain name")


class Vocabulary(BaseModel):
    """Vocabulary information for a concept."""
    
    id: str = Field(..., description="Vocabulary ID")
    name: str = Field(..., description="Vocabulary name")


class ConceptClass(BaseModel):
    """Concept class information."""
    
    id: str = Field(..., description="Concept class ID")
    name: str = Field(..., description="Concept class name")


class ConceptType(str, Enum):
    """Concept standard type."""
    
    STANDARD = "S"
    CLASSIFICATION = "C"
    NON_STANDARD = ""


class Concept(BaseModel):
    """Basic concept information returned in search results."""
    
    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain_id: str = Field(..., description="Domain ID")
    vocabulary_id: str = Field(..., description="Vocabulary ID")
    concept_class_id: str = Field(..., description="Concept class ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    concept_code: str = Field(..., description="Concept code")
    invalid_reason: Optional[str] = Field(None, description="Invalid reason")
    domain: Domain = Field(..., description="Domain object")
    vocabulary: Vocabulary = Field(..., description="Vocabulary object")
    concept_class: ConceptClass = Field(..., description="Concept class object")
    valid_start_date: str = Field(..., description="Valid start date")
    valid_end_date: str = Field(..., description="Valid end date")


class ConceptSearchResponse(BaseModel):
    """Response from the /concepts search endpoint."""
    
    content: List[Concept] = Field(..., description="List of concept results")
    pageable: Dict[str, Any] = Field(..., description="Pagination information")
    total_elements: int = Field(
        ..., description="Total number of results", alias="totalElements"
    )
    last: bool = Field(..., description="Whether this is the last page")
    total_pages: int = Field(
        ..., description="Total number of pages", alias="totalPages"
    )
    sort: Dict[str, Any] = Field(..., description="Sort information")
    first: bool = Field(..., description="Whether this is the first page")
    size: int = Field(..., description="Page size")
    number: int = Field(..., description="Page number")
    number_of_elements: int = Field(
        ..., description="Number of elements in this page", alias="numberOfElements"
    )
    empty: bool = Field(..., description="Whether the result is empty")


class ConceptDetails(BaseModel):
    """Detailed concept information from the /concepts/{id} endpoint."""
    
    id: int = Field(..., description="Concept ID")
    name: str = Field(..., description="Concept name")
    domain_id: str = Field(..., description="Domain ID")
    vocabulary_id: str = Field(..., description="Vocabulary ID")
    concept_class_id: str = Field(..., description="Concept class ID")
    standard_concept: Optional[ConceptType] = Field(
        None, description="Standard concept flag"
    )
    concept_code: str = Field(..., description="Concept code")
    invalid_reason: Optional[str] = Field(None, description="Invalid reason")
    domain: Domain = Field(..., description="Domain object")
    vocabulary: Vocabulary = Field(..., description="Vocabulary object")
    concept_class: ConceptClass = Field(..., description="Concept class object")
    valid_start_date: str = Field(..., description="Valid start date")
    valid_end_date: str = Field(..., description="Valid end date")
    # Additional fields specific to details
    synonyms: Optional[List[str]] = Field(None, description="Concept synonyms")
    additional_information: Optional[Dict[str, Any]] = Field(
        None, description="Additional information"
    )


class RelationshipItem(BaseModel):
    """Information about a relationship between concepts."""
    
    relationship_id: str = Field(..., description="Relationship ID")
    relationship_name: str = Field(..., description="Relationship name")
    relationship_concept_id: int = Field(..., description="Relationship concept ID")


class ConceptRelationship(BaseModel):
    """Response from the /concepts/{id}/relationships endpoint."""
    
    concept_id: int = Field(..., description="Concept ID")
    relationships: List[RelationshipItem] = Field(
        ..., description="List of relationships"
    )


class GraphNode(BaseModel):
    """Node in the concept relationship graph."""
    
    id: int = Field(..., description="Node ID")
    name: str = Field(..., description="Node name")
    concept_id: int = Field(..., description="Concept ID")
    domain_id: str = Field(..., description="Domain ID")
    standard_concept: Optional[ConceptType] = Field(None, description="Standard concept flag")


class GraphEdge(BaseModel):
    """Edge in the concept relationship graph."""
    
    source: int = Field(..., description="Source node ID")
    target: int = Field(..., description="Target node ID")
    relationship_id: str = Field(..., description="Relationship ID")


class ConceptRelationsGraph(BaseModel):
    """Response from the /concepts/{id}/relations endpoint."""
    
    nodes: List[GraphNode] = Field(..., description="Graph nodes")
    edges: List[GraphEdge] = Field(..., description="Graph edges")


# Re-export models
__all__ = [
    "Concept",
    "ConceptClass",
    "ConceptDetails",
    "ConceptRelationsGraph",
    "ConceptRelationship",
    "ConceptSearchResponse",
    "ConceptType",
    "Domain",
    "GraphEdge",
    "GraphNode",
    "RelationshipItem",
    "Vocabulary",
]

```

## Folder: build/bdist.macosx-15.5-arm64

## Folder: athena_client.egg-info

### File: `athena_client/athena_client.egg-info/SOURCES.txt`
<a name="athena_client-athena_clientegg-info-sourcestxt"></a>
```text
README.md
pyproject.toml
setup.py
athena_client/__init__.py
athena_client/async_client.py
athena_client/auth.py
athena_client/cli.py
athena_client/client.py
athena_client/exceptions.py
athena_client/http.py
athena_client/query.py
athena_client/search_result.py
athena_client/settings.py
athena_client.egg-info/PKG-INFO
athena_client.egg-info/SOURCES.txt
athena_client.egg-info/dependency_links.txt
athena_client.egg-info/entry_points.txt
athena_client.egg-info/requires.txt
athena_client.egg-info/top_level.txt
athena_client/models/__init__.py
athena_client/utils/__init__.py
tests/test_query.py
tests/test_search_result.py
```

### File: `athena_client/athena_client.egg-info/dependency_links.txt`
<a name="athena_client-athena_clientegg-info-dependency_linkstxt"></a>
```text


```

### File: `athena_client/athena_client.egg-info/entry_points.txt`
<a name="athena_client-athena_clientegg-info-entry_pointstxt"></a>
```text
[console_scripts]
athena = athena_client.cli:main

```

### File: `athena_client/athena_client.egg-info/requires.txt`
<a name="athena_client-athena_clientegg-info-requirestxt"></a>
```text
requests>=2.25.0
urllib3>=1.26.0
backoff>=1.10.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
orjson>=3.9.0

[all]
httpx>=0.18.0
pandas>=1.3.0
click>=8.0.0
rich>=10.0.0
pyyaml>=6.0
cryptography>=36.0.0

[async]
httpx>=0.18.0

[cli]
click>=8.0.0
rich>=10.0.0

[crypto]
cryptography>=36.0.0

[dev]
ruff>=0.4.0
mypy>=1.10
pip-audit>=2.6
pytest>=8.2
pytest-cov>=5.0
pytest-asyncio[mode-auto]>=0.23
hypothesis>=6.103
vcrpy>=6.0
rich>=13.7
build>=1.2
twine>=5.1
pytest-benchmark>=4.0
bandit>=1.7.5
cyclonedx-python-lib>=5.2.0
types-requests
types-PyYAML
pandas-stubs

[pandas]
pandas>=1.3.0

[yaml]
pyyaml>=6.0

```

### File: `athena_client/athena_client.egg-info/top_level.txt`
<a name="athena_client-athena_clientegg-info-top_leveltxt"></a>
```text
athena_client

```
