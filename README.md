# athena-client

[![SBOM](https://img.shields.io/badge/SBOM-available-blue)](https://github.com/aandresalvarez/athena_client/blob/main/sbom.json)

An unofficial Python SDK for interacting with the OHDSI Athena Concepts API. Easily search, explore, and analyze medical concepts without any additional setup.  
Developed by Alvaro A. Alvarez P. (alvaro1@stanford.edu).  
This project is provided as-is, without warranty of any kind.

> **Looking for advanced concept exploration, mapping, and best practices?**
> See the [Concept Exploration Guide](https://github.com/aandresalvarez/athena_client/blob/main/CONCEPT_EXPLORATION_GUIDE.md) for a comprehensive tutorial on robust usage, advanced workflows, and real-world examples.

> **Responsible Usage Notice:**
> Please use this package responsibly. Avoid making excessive or automated requests to the Athena API, as this may result in your IP being rate-limited or blocked by the API provider. Always use filters and limits where possible, and respect the terms of service of the OHDSI Athena API.

## Installation

### Lightweight Installation (Recommended)

For core functionality with CLI and minimal dependencies:

```bash
pip install athena-client
```

This installs the essential dependencies (8 packages) needed for basic Athena API operations and command-line interface.

### Full Installation

For all features including CLI, pandas support, and database integration:

```bash
pip install "athena-client[full]"
```

### Individual Extras

Install additional features you need:

```bash
pip install "athena-client[pandas]"   # pandas DataFrame support  
pip install "athena-client[yaml]"     # YAML format support
pip install "athena-client[crypto]"   # HMAC authentication
pip install "athena-client[db]"       # Database integration
```

### Database-Specific Installation

For specific database integrations:

```bash
pip install "athena-client[postgres]"  # PostgreSQL support
pip install "athena-client[bigquery]"  # Google BigQuery support
```

---

## Quick Start

```python
from athena_client import Athena

# Initialize Athena client (uses public Athena  by default)
athena = Athena()

# For custom servers, specify the base_url:
# athena = Athena(base_url="https://your-athena-server.com/api/v1")

# Search for concepts
results = athena.search("aspirin")

# Different ways to handle results
concept_list = results.all()
top_three = results.top(3)
as_json = results.to_json()
# as_df = results.to_df()  # Requires: pip install "athena-client[pandas]"

# Detailed information for a specific concept
details = athena.details(concept_id=1127433)

# Concept relationships
relationships = athena.relationships(concept_id=1127433)

# Concept graph
graph = athena.graph(concept_id=1127433, depth=3)

# Comprehensive summary
summary = athena.summary(concept_id=1127433)
```

> **💡 Try the lightweight demo:** `python examples/lightweight_demo.py` to see what works with minimal dependencies.
> **🔧 Try the server configuration demo:** `python examples/server_configuration_demo.py` to see how to connect to different Athena servers.

---

## Advanced Features

### Query DSL for Complex Searches

Build sophisticated queries using the Query DSL:

```python
from athena_client.query import Q

# Basic query types
q1 = Q.term("diabetes")           # Term search
q2 = Q.phrase("heart attack")     # Phrase search  
q3 = Q.exact('"Myocardial Infarction"')  # Exact match
q4 = Q.wildcard("aspir*")         # Wildcard search

# Complex combinations
complex_query = (Q.term("diabetes") & Q.term("type 2")) | Q.term("T2DM")
fuzzy_query = Q.term("aspirin").fuzzy(0.8)  # Fuzzy matching

# Use in search
results = athena.search(complex_query)
```

### Advanced SearchResult Features

The `SearchResult` class provides rich functionality:

```python
# Pagination
next_page = results.next_page()
prev_page = results.previous_page()

# Pagination info
print(f"Total elements: {results.total_elements}")
print(f"Total pages: {results.total_pages}")
print(f"Current page: {results.current_page}")
print(f"Page size: {results.page_size}")

# Facets and metadata
facets = results.facets

# Iteration and indexing
for concept in results:  # Iterate over concepts
    print(concept.name)

concept = results[0]  # Index access
```

### Progress Tracking for Large Queries

The library automatically handles large queries with progress tracking:

```python
# Large queries show progress automatically
results = athena.search("pain")  # Shows progress bar

# Custom progress tracking
from athena_client.utils import progress_context

with progress_context(total=1000, description="Searching..."):
    results = athena.search("large query")
```

### Advanced CLI Usage

The CLI supports powerful filtering and output options:

```bash
# Advanced search with filters
athena search "aspirin" --fuzzy --domain Drug --vocabulary RxNorm --limit 10

# Relationships with filters
athena relationships 1127433 --relationship-id "Maps to" --only-standard

# Graph with custom parameters
athena graph 1127433 --depth 3 --zoom-level 4

# Multiple output formats
athena search "aspirin" --output json --limit 5
athena search "aspirin" --output csv | tail -n +2 > aspirin.csv
```

### Concept Exploration (Advanced)

For advanced concept discovery and mapping:

```python
import asyncio
from athena_client.concept_explorer import create_concept_explorer

async def explore_concepts():
    explorer = create_concept_explorer(athena)
    
    # Find standard concepts through exploration
    results = await explorer.find_standard_concepts(
        query="headache",
        max_exploration_depth=2,
        vocabulary_priority=['SNOMED', 'RxNorm']
    )
    
    # Map concepts with confidence scores
    mappings = await explorer.map_to_standard_concepts(
        query="migraine",
        target_vocabularies=['SNOMED'],
        confidence_threshold=0.7
    )
    
    # Get alternative query suggestions
    suggestions = await explorer.suggest_alternative_queries("heart attack")

asyncio.run(explore_concepts())
```

> **📚 For detailed concept exploration examples and best practices, see the [Concept Exploration Guide](https://github.com/aandresalvarez/athena_client/blob/main/CONCEPT_EXPLORATION_GUIDE.md).**

---

## Server Configuration

The athena-client can connect to different Athena API servers. By default, it connects to the public OHDSI Athena API at `https://athena.ohdsi.org/api/v1`.

### Connecting to Different Servers

#### Method 1: Direct Configuration (Recommended)

```python
from athena_client import Athena

# Connect to a custom Athena server
athena = Athena(base_url="https://your-athena-server.com/api/v1")

# Connect with authentication
athena = Athena(
    base_url="https://your-athena-server.com/api/v1",
    token="your-bearer-token"
)

# Connect with HMAC authentication
athena = Athena(
    base_url="https://your-athena-server.com/api/v1",
    client_id="your-client-id",
    private_key="your-private-key"
)
```

#### Method 2: Environment Variables

Set environment variables for persistent configuration:

```bash
# Set the base URL
export ATHENA_BASE_URL="https://your-athena-server.com/api/v1"

# Set authentication (optional)
export ATHENA_TOKEN="your-bearer-token"
export ATHENA_CLIENT_ID="your-client-id"
export ATHENA_PRIVATE_KEY="your-private-key"
```

#### Method 3: .env File

Create a `.env` file in your project directory:

```env
ATHENA_BASE_URL=https://your-athena-server.com/api/v1
ATHENA_TOKEN=your-bearer-token
ATHENA_CLIENT_ID=your-client-id
ATHENA_PRIVATE_KEY=your-private-key
```

### CLI Server Configuration

Configure the CLI to use a different server:

```bash
# Use command-line options (--base-url applies to all commands)
athena --base-url "https://your-athena-server.com/api/v1" search "aspirin"
athena --base-url "https://your-athena-server.com/api/v1" details 1127433

# Use environment variables
export ATHENA_BASE_URL="https://your-athena-server.com/api/v1"
athena search "aspirin"
```

### Advanced Configuration Options

The client supports additional configuration for different server environments:

```python
from athena_client import Athena

# Custom timeout and retry settings for slower servers
athena = Athena(
    base_url="https://your-athena-server.com/api/v1",
    timeout=60,           # 60 second timeout
    max_retries=5,        # 5 retry attempts
    enable_throttling=True  # Respect server rate limits
)

# Disable throttling for local development servers
athena = Athena(
    base_url="http://localhost:8080/api/v1",
    enable_throttling=False
)
```

### Configuration Precedence

Settings are applied in this order (highest to lowest priority):

1. **Direct parameters** in `Athena()` constructor
2. **Environment variables** (e.g., `ATHENA_BASE_URL`)
3. **Default values** (public OHDSI Athena API)

### Common Server Scenarios

| Scenario | Configuration |
|----------|---------------|
| **Public OHDSI Athena** | `Athena()` (default) |
| **Private Athena Instance** | `Athena(base_url="https://your-server.com/api/v1")` |
| **Local Development** | `Athena(base_url="http://localhost:8080/api/v1")` |
| **Authenticated Server** | `Athena(base_url="...", token="...")` |
| **High-Latency Network** | `Athena(base_url="...", timeout=120, max_retries=5)` |

---

## CLI Quick Start

Athena CLI allows rapid concept search and exploration:

```bash
# Install CLI first: pip install "athena-client[cli]"
athena search "aspirin" --limit 3 --output json
athena details 1127433
athena relationships 1127433
athena graph 1127433 --depth 3
athena summary 1127433

# For custom servers, use --base-url:
# athena --base-url "https://your-athena-server.com/api/v1" search "aspirin"
```

### CLI Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `search` | Search for concepts | `athena search "aspirin" --limit 5` |
| `details` | Get concept details | `athena details 1127433` |
| `relationships` | Get concept relationships | `athena relationships 1127433` |
| `graph` | Get concept graph | `athena graph 1127433 --depth 2` |
| `summary` | Get comprehensive summary | `athena summary 1127433` |
| `generate-set` | Generate concept set (experimental) | `athena generate-set "diabetes"` |

### Output Formats

The CLI supports multiple output formats:

```bash
# JSON output
athena search "aspirin" --output json

# YAML output (requires: pip install "athena-client[yaml]")
athena search "aspirin" --output yaml

# CSV output
athena search "aspirin" --output csv

# Pretty table (default)
athena search "aspirin" --output pretty

# Export to file
athena search "aspirin" --output json | tail -n +2 > aspirin.json
```

---

## Dependency Comparison

| Installation Method | Dependencies | Size | Features |
|-------------------|-------------|------|----------|
| `pip install athena-client` | 8 packages | ~4MB | Core API functionality + Command-line interface |
| `pip install "athena-client[pandas]"` | +1 package | ~15MB | + DataFrame support |
| `pip install "athena-client[yaml]"` | +1 package | ~1MB | + YAML format support |
| `pip install "athena-client[crypto]"` | +1 package | ~4MB | + HMAC authentication |
| `pip install "athena-client[db]"` | +2 packages | ~3MB | + Database integration |
| `pip install "athena-client[full]"` | +5 packages | ~25MB | All features |

---

## Experimental: Database Integration (Advanced Users)

> **Warning:** Database integration features are experimental, subject to change, and may encounter errors.

Experimental database integration allows validation and concept set generation against your local OMOP database. Use these features cautiously.

### Installation for Database Support

For specific database integrations:

* PostgreSQL:

  ```bash
  pip install "athena-client[postgres]"
  ```

* Google BigQuery:

  ```bash
  pip install "athena-client[bigquery]"
  ```

* All database support:

  ```bash
  pip install "athena-client[db]"
  ```

### Reducing Dependency Conflicts (Advanced)

To minimize dependency issues:

* Use specific extras when installing.
* For BigQuery integration, use Python 3.9 and SQLAlchemy < 1.5.0.

### Database Usage Example

```python
import asyncio
from athena_client import Athena

DB_CONNECTION_STRING = "postgresql://user:pass@localhost/omop_cdm"

async def main():
    athena = Athena()
    concept_set = await athena.generate_concept_set(
        query="Type 2 Diabetes",
        db_connection_string=DB_CONNECTION_STRING
    )
    print(concept_set)

asyncio.run(main())
```

---

## Experimental CLI Database Example

```bash
export OMOP_DB_CONNECTION="postgresql://user:pass@localhost/omop"
athena generate-set "Type 2 Diabetes" --output json
```

---

## Error Handling & Retry Logic

The library provides robust error handling and automatic retry:

```python
from athena_client import Athena

# Automatic retry on network errors
athena = Athena(max_retries=3, timeout=30)

# Per-call retry configuration
results = athena.search(
    "aspirin",
    auto_retry=True,
    max_retries=5,
    retry_delay=2.0,
    show_progress=True
)

# Disable retry for specific calls
results = athena.search("aspirin", auto_retry=False)
```

### Error Types

- **NetworkError**: DNS, connection, socket issues
- **TimeoutError**: Request timeout
- **ClientError**: 4xx HTTP status codes
- **ServerError**: 5xx HTTP status codes
- **AuthenticationError**: 401/403
- **RateLimitError**: 429
- **ValidationError**: Data validation
- **APIError**: API-specific errors

> **📚 For detailed error handling examples and troubleshooting, see the [Concept Exploration Guide](https://github.com/aandresalvarez/athena_client/blob/main/CONCEPT_EXPLORATION_GUIDE.md).**

---

## Troubleshooting Common Issues

* **Dependency installation problems:** Ensure Python version compatibility and correct extras.
* **PostgreSQL build errors:** Install PostgreSQL development tools (`brew install postgresql` on macOS).
* **BigQuery SQLAlchemy conflicts:** Only use Python 3.9 with BigQuery integration.
* **Connection issues:** Verify your server URL and network connectivity. Use `--base-url` or `ATHENA_BASE_URL` environment variable to specify custom servers.

---

## Exporting CLI Results to Files (JSON, YAML, CSV)

You can export CLI search results to various formats:

```bash
# For YAML support: pip install "athena-client[yaml]"

athena search "aspirin" --output json | tail -n +2 > aspirin_concepts.json
athena search "aspirin" --output yaml | tail -n +2 > aspirin_concepts.yaml
athena search "aspirin" --output csv  | tail -n +2 > aspirin_concepts.csv
```

> **Note:** The `tail -n +2` removes warning lines (such as large query warnings) to ensure the output file is valid for the chosen format.

---

## Version Compatibility

* **Python:** >= 3.9, < 3.13
* **SQLAlchemy:** >= 1.4.0 (BigQuery limited to <1.5.0)
* **pandas:** >= 1.3.0, < 3.0.0
* **pydantic:** >= 2.0.0
* **httpx:** >= 0.18.0
* **cryptography:** >= 36.0.0

---

## Examples & Demos

The library includes several example scripts to demonstrate its capabilities:

- **`examples/lightweight_demo.py`** - Core functionality with minimal dependencies
- **`examples/server_configuration_demo.py`** - Connecting to different Athena servers
- **`examples/error_handling_demo.py`** - Error handling and retry logic
- **`examples/retry_throttling_demo.py`** - Advanced retry and throttling features
- **`examples/large_query_demo.py`** - Handling large queries with progress tracking
- **`examples/graph_demo.py`** - Concept graph exploration and analysis
- **`examples/concept_exploration_demo.py`** - Advanced concept discovery features

Run any example with:
```bash
python examples/example_name.py
```

---

## What's Next?

- **📚 [Concept Exploration Guide](https://github.com/aandresalvarez/athena_client/blob/main/CONCEPT_EXPLORATION_GUIDE.md)** - Advanced usage, best practices, and real-world examples
- **🔧 [Contributing Guide](https://github.com/aandresalvarez/athena_client/blob/main/CONTRIBUTING.md)** - How to contribute to the project
- **🗺️ [Roadmap](https://github.com/aandresalvarez/athena_client/blob/main/ROADMAP.md)** - Planned features and enhancements
- **📦 [Lightweight Installation Guide](https://github.com/aandresalvarez/athena_client/blob/main/LIGHTWEIGHT_INSTALLATION.md)** - Detailed dependency management


