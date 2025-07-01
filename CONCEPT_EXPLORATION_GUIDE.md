# Athena Client: Complete Usage & Concept Exploration Guide

This guide is your comprehensive resource for using the `athena-client` Python SDK with the OHDSI Athena Concepts API. It covers installation, usage, CLI, advanced features, robust concept exploration, error handling, configuration, performance, and real-world best practices.

---

## 1. Installation & Environment

Install the core package:

```bash
pip install athena-client
```

Or, for explicit minimal dependencies:

```bash
pip install "athena-client[core]"
```

### Optional Features & Extras
- **Database support:**
  - PostgreSQL: `pip install "athena-client[postgres]"`
  - BigQuery: `pip install "athena-client[bigquery]"` (Python 3.9 only)
- **All features:**
  - `pip install "athena-client[all]"`
- **Other extras:**
  - CLI: `pip install athena-client[cli]`
  - Async: `pip install athena-client[async]`
  - Pandas: `pip install athena-client[pandas]`
  - YAML: `pip install athena-client[yaml]`
  - Crypto: `pip install athena-client[crypto]`

> **BigQuery users:** Use Python 3.9 and `sqlalchemy<1.5.0` for compatibility.

#### Reducing Dependency Conflicts
- Install only the extras you need.
- For BigQuery, use Python 3.9 and compatible SQLAlchemy.
- For maximum compatibility, use the latest Python and dependencies.

---

## 2. Quick Start (Python API)

```python
from athena_client import Athena
athena = Athena()
results = athena.search("aspirin")
print(results.all())
```

### Output Formats
- `results.all()`: List of Pydantic models
- `results.top(3)`: First three results
- `results.to_list()`: List of dicts
- `results.to_json()`: JSON string
- `results.to_df()`: pandas DataFrame

### Other Core Methods
```python
# Get details for a concept
details = athena.details(concept_id=1127433)
# Get relationships
rels = athena.relationships(concept_id=1127433)
# Get graph
graph = athena.graph(concept_id=1127433, depth=5)
# Get summary
summary = athena.summary(concept_id=1127433)
```

---

## 3. Command-Line Interface (CLI)

Install the CLI extra and use the `athena` command:

```bash
athena search "aspirin"
athena search "aspirin" --limit 3
athena search "aspirin" --output json
athena details 1127433
athena relationships 1127433
athena graph 1127433 --depth 3
athena summary 1127433
athena search "diabetes" --domain Condition --vocabulary SNOMED
athena search "aspirin" --output json > aspirin_concepts.json
```

---

## 4. Advanced: Database Integration (Experimental)

Validate concept sets against your local OMOP database.

**Python Example:**
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

**CLI Example:**
```bash
export OMOP_DB_CONNECTION="postgresql://user:pass@localhost/omop"
athena generate-set "Type 2 Diabetes" --output json
```

---

## 5. Concept Exploration: Finding Standard Concepts

Medical terminology is complex. `athena-client` provides advanced exploration to find standard concepts, synonyms, relationships, and cross-references.

### Why Concept Exploration?
- **Standard concepts**: Canonical representations
- **Non-standard concepts**: Common terms
- **Synonyms**: Alternative names
- **Relationships**: Connect concepts across vocabularies
- **Cross-references**: Map between coding systems

### Basic Exploration
```python
import asyncio
from athena_client.async_client import AthenaAsyncClient
from athena_client import create_concept_explorer
client = AthenaAsyncClient()
explorer = create_concept_explorer(client)
async def explore_concepts():
    results = await explorer.find_standard_concepts(
        query="headache",
        max_exploration_depth=2,
        initial_seed_limit=10,
        include_synonyms=True,
        include_relationships=True,
        vocabulary_priority=['SNOMED', 'RxNorm', 'ICD10']
    )
    print(f"Direct matches: {len(results['direct_matches'])}")
    print(f"Synonym matches: {len(results['synonym_matches'])}")
    print(f"Relationship matches: {len(results['relationship_matches'])}")
    print(f"Cross-references: {len(results['cross_references'])}")
asyncio.run(explore_concepts())
```

### Mapping to Standard Concepts with Confidence Scores
```python
async def map_concepts():
    mappings = await explorer.map_to_standard_concepts(
        query="migraine",
        target_vocabularies=['SNOMED', 'RxNorm'],
        confidence_threshold=0.5
    )
    for mapping in mappings:
        concept = mapping['concept']
        confidence = mapping['confidence']
        path = mapping['exploration_path']
        print(f"Concept: {concept.name}")
        print(f"Vocabulary: {concept.vocabulary}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Discovery path: {path}\n")
asyncio.run(map_concepts())
```

### Alternative Query Suggestions
```python
suggestions = explorer.suggest_alternative_queries(query="heart attack", max_suggestions=8)
print("Alternative suggestions:")
for suggestion in suggestions:
    print(f"  - {suggestion}")
```

### Concept Hierarchy Exploration
```python
hierarchy = explorer.get_concept_hierarchy(concept_id=12345, max_depth=3)
print(f"Root concept: {hierarchy['root_concept'].name}")
print(f"Parent relationships: {len(hierarchy['parents'])}")
print(f"Child relationships: {len(hierarchy['children'])}")
print(f"Sibling relationships: {len(hierarchy['siblings'])}")
```

### Comprehensive Workflow Example
```python
import asyncio
from athena_client.async_client import AthenaAsyncClient
from athena_client import create_concept_explorer
async def find_standard_concepts_workflow(query):
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    direct_results = client.search_concepts(query, page_size=10)
    direct_standard = [c for c in direct_results['content'] if c.standardConcept == "Standard"]
    if direct_standard:
        print(f"✅ Found {len(direct_standard)} standard concepts directly")
        return direct_standard
    print("🔍 Exploring for standard concepts...")
    exploration_results = await explorer.find_standard_concepts(
        query=query,
        max_exploration_depth=3,
        initial_seed_limit=10,
        include_synonyms=True,
        include_relationships=True
    )
    mappings = await explorer.map_to_standard_concepts(
        query=query,
        confidence_threshold=0.4
    )
    if mappings:
        print(f"✅ Found {len(mappings)} high-confidence mappings")
        return [m['concept'] for m in mappings]
    print("💡 Trying alternative queries...")
    suggestions = explorer.suggest_alternative_queries(query, max_suggestions=5)
    for suggestion in suggestions:
        test_results = client.search_concepts(suggestion, page_size=5)
        standard_found = [c for c in test_results['content'] if c.standardConcept == "Standard"]
        if standard_found:
            print(f"✅ Found standard concepts with suggestion: '{suggestion}'")
            return standard_found
    print("❌ No standard concepts found")
    return []
async def main():
    standard_concepts = await find_standard_concepts_workflow("myocardial infarction")
    print(f"Found {len(standard_concepts)} standard concepts")
asyncio.run(main())
```

### Advanced Configuration
```python
from athena_client.settings import get_settings
settings = get_settings()
settings.ATHENA_SEARCH_TIMEOUT_SECONDS = 60
settings.ATHENA_GRAPH_TIMEOUT_SECONDS = 90
settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS = 60
settings.ATHENA_DEFAULT_PAGE_SIZE = 50
settings.ATHENA_MAX_PAGE_SIZE = 1000
settings.ATHENA_LARGE_QUERY_THRESHOLD = 100
settings.ATHENA_SHOW_PROGRESS = True
settings.ATHENA_PROGRESS_UPDATE_INTERVAL = 2.0
```

### Use Cases
#### Clinical Decision Support
```python
async def clinical_decision_support():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    conditions = ["chest pain", "shortness of breath", "fever"]
    standard_concepts = {}
    for condition in conditions:
        mappings = await explorer.map_to_standard_concepts(
            condition, target_vocabularies=['SNOMED'], confidence_threshold=0.6)
        if mappings:
            standard_concepts[condition] = mappings[0]['concept']
    return standard_concepts
asyncio.run(clinical_decision_support())
```
#### Medication Mapping
```python
async def medication_mapping():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    medications = ["aspirin", "ibuprofen", "acetaminophen"]
    drug_concepts = {}
    for med in medications:
        mappings = await explorer.map_to_standard_concepts(
            med, target_vocabularies=['RxNorm'], confidence_threshold=0.5)
        if mappings:
            drug_concepts[med] = mappings[0]['concept']
    return drug_concepts
asyncio.run(medication_mapping())
```
#### Cross-Vocabulary Mapping
```python
async def cross_vocabulary_mapping():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    icd10_results = client.search_concepts("diabetes", vocabulary="ICD10")
    if icd10_results['content']:
        icd10_concept = icd10_results['content'][0]
        snomed_mappings = await explorer.map_to_standard_concepts(
            icd10_concept.name, target_vocabularies=['SNOMED'], confidence_threshold=0.7)
        return snomed_mappings
    return []
asyncio.run(cross_vocabulary_mapping())
```

### Best Practices for Exploration
- Start with direct search for speed
- Use confidence thresholds (0.5–0.7) for mapping
- Specify target vocabularies for relevance
- Explore relationships and synonyms for broader coverage
- Use alternative queries if no direct match
- Monitor and adjust timeout settings for complex queries

### Performance Considerations
- **Exploration depth**: 1–3 for most cases
- **Vocabulary filtering**: Reduces API calls
- **Confidence thresholds**: Focus on high-quality matches
- **Caching**: Implement for frequently used mappings

### Error Handling in Exploration
```python
try:
    mappings = await explorer.map_to_standard_concepts("diabetes")
    print(f"Found {len(mappings)} mappings")
except Exception as e:
    print(f"Exploration failed: {e}")
    results = client.search_concepts("diabetes")
    print(f"Direct search found {len(results['content'])} concepts")
```

---

## 6. Error Handling & Retry Logic

`athena-client` provides robust error handling and automatic retry:

```python
from athena_client import Athena
athena = Athena()
results = athena.search("aspirin")
print(f"Found {len(results.all())} concepts")
details = athena.details(concept_id=1127433)
print(f"Concept: {details.name}")
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

### Advanced Error Handling
```python
from athena_client.exceptions import NetworkError, APIError, ClientError
try:
    results = athena.search("aspirin")
except NetworkError as e:
    print(f"Network issue: {e}")
except APIError as e:
    print(f"API issue: {e}")
except ClientError as e:
    print(f"Client error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Disabling Auto-Retry
```python
results = athena.search("aspirin", auto_retry=False)
athena = Athena(max_retries=0)
```

### Retry Configuration
```python
athena = Athena(
    max_retries=5,
    retry_delay=2.0,
    enable_throttling=True,
    throttle_delay_range=(0.1, 0.5),
    timeout=30
)
results = athena.search("aspirin", max_retries=3, retry_delay=1.0)
```

### Detailed Retry Error Reporting
```python
try:
    results = athena.search("aspirin")
except RetryFailedError as e:
    print(f"Retry failed after {e.max_attempts} attempts")
    print(f"Last error: {e.last_error}")
    print(f"Retry history: {e.retry_history}")
```

---

## 7. Enhanced Large Query Handling

- **Automatic timeout adjustment** for query complexity
- **Progress tracking** for long operations
- **User-friendly warnings** for broad queries
- **Smart pagination** and validation
- **Memory-efficient processing** for large result sets
- **Configurable thresholds** for different query types

```python
results = athena.search("pain")  # Large query, progress bar shown
try:
    results = athena.search("aspirin", size=2000)  # Raises ValueError if size too large
except ValueError as e:
    print(e)
```

#### Configuration Example
```python
from athena_client.settings import get_settings
settings = get_settings()
settings.ATHENA_SEARCH_TIMEOUT_SECONDS = 60
settings.ATHENA_GRAPH_TIMEOUT_SECONDS = 90
settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS = 60
settings.ATHENA_DEFAULT_PAGE_SIZE = 50
settings.ATHENA_MAX_PAGE_SIZE = 1000
settings.ATHENA_LARGE_QUERY_THRESHOLD = 100
settings.ATHENA_SHOW_PROGRESS = True
settings.ATHENA_PROGRESS_UPDATE_INTERVAL = 2.0
```

#### Best Practices for Large Queries
- Use specific search terms
- Add filters (domain, vocabulary)
- Use smaller page sizes for large queries
- Enable progress tracking
- Adjust timeout settings for complex operations

---

## 8. Real-World Use Cases

- **Clinical Decision Support**: Map symptoms to standard concepts
- **Medication Mapping**: Map drug names to RxNorm
- **Cross-Vocabulary Mapping**: Map ICD10 to SNOMED
- **Data Quality**: Validate concept sets against OMOP
- **Research Analytics**: Build robust, reproducible concept sets

---

## 9. Troubleshooting & Compatibility

- **Editable install fails:** Upgrade pip and setuptools, check `pyproject.toml`
- **psycopg2-binary errors:** On macOS, run `brew install postgresql`
- **BigQuery install fails:** Use Python 3.9 and compatible SQLAlchemy
- **Python version errors:** Use `pyenv` or `.python-version` to enforce Python 3.9 for BigQuery

### Version Compatibility
- **Python**: >= 3.9, < 3.13
- **SQLAlchemy**: >= 1.4.0 (1.4.x and 2.x supported, but BigQuery needs <1.5.0)
- **pandas**: >= 1.3.0, < 3.0.0
- **pydantic**: >= 2.0.0
- **httpx**: >= 0.18.0
- **cryptography**: >= 36.0.0

---

For more details, see the [README](./README.md) or the official documentation. This guide is designed to be your one-stop resource for robust, production-ready concept exploration and Athena API integration.
