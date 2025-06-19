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

## Error Handling

The athena-client provides **automatic error handling and recovery** out of the box. You don't need to implement try-catch blocks - the client handles errors gracefully and provides clear, actionable messages:

```python
from athena_client import Athena

athena = Athena()

# Automatic error handling - no try-catch needed!
results = athena.search("aspirin")
print(f"Found {len(results.all())} concepts")

# If there are network issues, the client automatically retries
# If there are API errors, you get clear, actionable messages
details = athena.details(concept_id=1127433)
print(f"Concept: {details.name}")
```

### What Happens Automatically

✅ **Network errors** are automatically retried (up to 3 attempts)  
✅ **API errors** provide clear, actionable messages  
✅ **Timeout issues** are handled with exponential backoff  
✅ **Invalid parameters** are caught with helpful suggestions  
✅ **Missing resources** are reported with context  

### Advanced Error Handling (Optional)

If you want more control, you can still use try-catch blocks:

```python
from athena_client import Athena
from athena_client.exceptions import NetworkError, APIError, ClientError

athena = Athena()

try:
    results = athena.search("aspirin")
    print(f"Found {len(results.all())} concepts")
except NetworkError as e:
    print(f"Network issue: {e}")
    # Error includes troubleshooting suggestions
except APIError as e:
    print(f"API issue: {e}")
    # Specific API error messages with context
except ClientError as e:
    print(f"Client error: {e}")
    # HTTP 4xx errors with status codes
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Disabling Auto-Retry

If you prefer to handle retries yourself, you can disable automatic retry:

```python
# Disable automatic retry for this call
results = athena.search("aspirin", auto_retry=False)

# Or disable for all calls
athena = Athena(max_retries=0)
```

### Advanced Retry Configuration

Developers have fine-grained control over retry behavior:

```python
# Configure retry settings at client level
athena = Athena(
    max_retries=5,                    # Maximum retry attempts
    retry_delay=2.0,                  # Fixed delay between retries (seconds)
    enable_throttling=True,           # Enable request throttling
    throttle_delay_range=(0.1, 0.5),  # Throttling delay range (min, max)
    timeout=30                        # Request timeout
)

# Override retry settings for specific calls
results = athena.search(
    "aspirin",
    max_retries=3,      # Override max retries for this call
    retry_delay=1.0     # Override retry delay for this call
)
```

### Detailed Retry Error Reporting

When retries fail, you get comprehensive error information:

```python
try:
    results = athena.search("aspirin")
except RetryFailedError as e:
    print(f"Retry failed after {e.max_attempts} attempts")
    print(f"Last error: {e.last_error}")
    print(f"Retry history: {e.retry_history}")
    # Error includes detailed retry information and troubleshooting
```

### Retry Configuration Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `max_retries` | Maximum retry attempts for network errors | 3 | `max_retries=5` |
| `retry_delay` | Fixed delay between retries (overrides exponential backoff) | None | `retry_delay=2.0` |
| `enable_throttling` | Enable request throttling to prevent overwhelming server | True | `enable_throttling=False` |
| `throttle_delay_range` | Range of delays for throttling (min, max) in seconds | (0.1, 0.3) | `throttle_delay_range=(0.2, 0.5)` |
| `timeout` | Request timeout in seconds | 15 | `timeout=30` |

### Error Types

- **NetworkError**: DNS, connection, socket issues
- **TimeoutError**: Request timeout issues  
- **ClientError**: 4xx HTTP status codes
- **ServerError**: 5xx HTTP status codes
- **AuthenticationError**: 401/403 authentication issues
- **RateLimitError**: 429 rate limiting issues
- **ValidationError**: Data validation failures
- **APIError**: API-specific error responses

### Error Message Features

✅ **Clear explanations** of what went wrong  
✅ **Context** about where the error occurred  
✅ **Specific troubleshooting suggestions**  
✅ **Error codes** for programmatic handling  
✅ **User-friendly language** (not technical jargon)  
✅ **Automatic retry** for recoverable errors

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
