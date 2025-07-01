# athena-client

[![SBOM](https://img.shields.io/badge/SBOM-available-blue)](sbom.json)

A production-ready Python SDK for interacting with the OHDSI Athena Concepts API. Easily search, explore, and analyze medical concepts without any additional setup.

> **Looking for advanced concept exploration, mapping, and best practices?**
> See the [Concept Exploration Guide](CONCEPT_EXPLORATION_GUIDE.md) for a comprehensive tutorial on robust usage, advanced workflows, and real-world examples.

## Installation

### Basic Installation (Recommended)

For standard use, install with:

```bash
pip install athena-client
```

This provides essential Athena API functionalities like concept search and exploration without database integration.

Alternatively, explicitly specify:

```bash
pip install "athena-client[core]"
```

Both methods offer the same functionality.

---

## Quick Start

```python
from athena_client import Athena

# Initialize Athena client (uses public Athena API by default)
athena = Athena()

# Search for concepts
results = athena.search("aspirin")

# Different ways to handle results
concept_list = results.all()
top_three = results.top(3)
as_json = results.to_json()
as_df = results.to_df()

# Detailed information for a specific concept
details = athena.details(concept_id=1127433)

# Concept relationships
relationships = athena.relationships(concept_id=1127433)

# Concept graph
graph = athena.graph(concept_id=1127433, depth=3)

# Comprehensive summary
summary = athena.summary(concept_id=1127433)
```

---

## CLI Quick Start

Athena CLI allows rapid concept search and exploration:

```bash
athena search "aspirin" --limit 3 --output json
athena details 1127433
athena relationships 1127433
athena graph 1127433 --depth 3
athena summary 1127433
```

---

## Optional Extras

Additional functionalities can be installed separately:

```bash
pip install athena-client[cli]      # Command-line interface
pip install athena-client[async]    # Async client support
pip install athena-client[pandas]   # pandas DataFrame support
pip install athena-client[yaml]     # YAML format support
pip install athena-client[crypto]   # HMAC authentication
pip install athena-client[all]      # All optional dependencies
```

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

## Troubleshooting Common Issues

* **Dependency installation problems:** Ensure Python version compatibility and correct extras.
* **PostgreSQL build errors:** Install PostgreSQL development tools (`brew install postgresql` on macOS).
* **BigQuery SQLAlchemy conflicts:** Only use Python 3.9 with BigQuery integration.

---

## Version Compatibility

* **Python:** >= 3.9, < 3.13
* **SQLAlchemy:** >= 1.4.0 (BigQuery limited to <1.5.0)
* **pandas:** >= 1.3.0, < 3.0.0
* **pydantic:** >= 2.0.0
* **httpx:** >= 0.18.0
* **cryptography:** >= 36.0.0

---

This README provides clarity on basic use, separates experimental features, and outlines recommended practices clearly.
