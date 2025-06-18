# athena-client

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

## Documentation

For complete documentation, visit: [https://athena-client.readthedocs.io](https://athena-client.readthedocs.io)

## License

MIT
