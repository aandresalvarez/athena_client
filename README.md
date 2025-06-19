# athena-client
[![SBOM](https://img.shields.io/badge/SBOM-available-blue)](sbom.json)

A production-ready Python SDK for the OHDSI Athena Concepts API.

## Installation

```bash
pip install athena-client
```

To enable database integration features for concept set generation, install the necessary extras:

**For PostgreSQL:**
```bash
pip install "athena-client[postgres]"
```

**For Google BigQuery:**
```bash
pip install "athena-client[bigquery]"
```

Other optional dependencies:
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

---

## Generating Validated Concept Sets

This feature bridges the gap between the public Athena API and your local OMOP database, allowing you to generate complete, analysis-ready concept sets that are validated against your specific vocabulary version.

### How It Works
1.  **Discover**: Uses the Athena API's powerful search to find candidate standard concepts for your query.
2.  **Validate**: Checks if those concepts exist and are marked as 'Standard' **in your local database**. This is crucial for aligning with your institution's vocabulary version.
3.  **Expand**: Queries your local `concept_ancestor` table to instantly find all descendant concepts, ensuring your set is complete.
4.  **Recover**: If the best concept from the API isn't in your local DB, it intelligently finds an alternative path using other candidates or local non-standard mappings.

### Usage Example
```python
import asyncio
from athena_client import Athena

# Your OMOP database connection string
# (You'll get this from your database administrator)
DB_CONNECTION_STRING = "postgresql://user:pass@localhost/omop_cdm"

async def main():
    athena = Athena()

    # Generate a concept set for "Type 2 Diabetes"
    concept_set = await athena.generate_concept_set(
        query="Type 2 Diabetes",
        db_connection_string=DB_CONNECTION_STRING
    )

    if concept_set["metadata"]["status"] == "SUCCESS":
        print(f"Success! Found {len(concept_set['concept_ids'])} concepts.")
        print(f"Strategy used: {concept_set['metadata']['strategy_used']}")
        for warning in concept_set['metadata'].get('warnings', []):
            print(f"Warning: {warning}")
    else:
        print(f"Failed: {concept_set['metadata']['reason']}")

asyncio.run(main())
```
The returned dictionary includes the `concept_ids` and `metadata` explaining how the set was generated and any warnings to consider.

### CLI Usage for Concept Sets
You can also generate concept sets directly from the command line.

```bash
# Set an environment variable with your connection string (optional, but convenient)
export OMOP_DB_CONNECTION="postgresql://user:pass@localhost/omop"

# Generate the concept set and output as JSON
athena generate-set "Type 2 Diabetes" --output json
```

---
***(New Section Ends Here)***

## Concept Exploration - Finding Standard Concepts

The athena-client provides advanced concept exploration capabilities to help you find standard concepts that might not appear directly in search results. This is particularly useful when working with medical terminology where standard concepts may be referenced through synonyms, relationships, or cross-references.

### Why Concept Exploration?

Medical terminology systems often have complex hierarchies where:
- **Standard concepts** are the preferred, canonical representations
- **Non-standard concepts** may be more commonly used terms
- **Synonyms** provide alternative names for the same concept
- **Relationships** connect related concepts across vocabularies
- **Cross-references** map concepts between different coding systems

The concept exploration functionality helps bridge the gap between user queries and standard medical concepts.

### Basic Concept Exploration

```python
import asyncio
from athena_client import Athena, create_concept_explorer
from athena_client.async_client import AthenaAsyncClient

# Create async client and explorer (recommended for best performance)
client = AthenaAsyncClient()
explorer = create_concept_explorer(client)

async def explore_concepts():
    # Find standard concepts through exploration
    results = await explorer.find_standard_concepts(
        query="headache",
        max_exploration_depth=2,
        initial_seed_limit=10,  # Control exploration scope
        include_synonyms=True,
        include_relationships=True,
        vocabulary_priority=['SNOMED', 'RxNorm', 'ICD10']
    )

    print(f"Direct matches: {len(results['direct_matches'])}")
    print(f"Synonym matches: {len(results['synonym_matches'])}")
    print(f"Relationship matches: {len(results['relationship_matches'])}")
    print(f"Cross-references: {len(results['cross_references'])}")

# Run the async function
asyncio.run(explore_concepts())
```

### Mapping to Standard Concepts with Confidence Scores

```python
async def map_concepts():
    # Map a query to standard concepts with confidence scoring
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
        print(f"Discovery path: {path}")
        print()

asyncio.run(map_concepts())
```

### Alternative Query Suggestions

When standard concepts aren't found directly, get alternative query suggestions:

```python
# Get alternative query suggestions
suggestions = explorer.suggest_alternative_queries(
    query="heart attack", 
    max_suggestions=8
)

print("Alternative suggestions:")
for suggestion in suggestions:
    print(f"  - {suggestion}")

# Test a suggestion
test_results = athena.search(suggestions[0], size=5)
standard_concepts = [c for c in test_results.all() if c.standardConcept == "Standard"]
print(f"Found {len(standard_concepts)} standard concepts")
```

### Concept Hierarchy Exploration

Explore the hierarchical relationships of concepts:

```python
# Get concept hierarchy
hierarchy = explorer.get_concept_hierarchy(
    concept_id=12345, 
    max_depth=3
)

print(f"Root concept: {hierarchy['root_concept'].name}")
print(f"Parent relationships: {len(hierarchy['parents'])}")
print(f"Child relationships: {len(hierarchy['children'])}")
print(f"Sibling relationships: {len(hierarchy['siblings'])}")

# Show parent concepts
for parent in hierarchy['parents'][:3]:
    print(f"  Parent: {parent.targetConceptName} ({parent.relationshipName})")
```

### Comprehensive Workflow Example

Here's a complete workflow for finding standard concepts:

```python
import asyncio
from athena_client.async_client import AthenaAsyncClient
from athena_client import create_concept_explorer

async def find_standard_concepts_workflow(query):
    """Comprehensive workflow for finding standard concepts."""
    
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    # Step 1: Try direct search first
    direct_results = client.search_concepts(query, page_size=10)
    direct_standard = [c for c in direct_results['content'] if c.standardConcept == "Standard"]
    
    if direct_standard:
        print(f"✅ Found {len(direct_standard)} standard concepts directly")
        return direct_standard
    
    # Step 2: Use concept exploration
    print("🔍 Exploring for standard concepts...")
    exploration_results = await explorer.find_standard_concepts(
        query=query,
        max_exploration_depth=3,
        initial_seed_limit=10,
        include_synonyms=True,
        include_relationships=True
    )
    
    # Step 3: Get high-confidence mappings
    mappings = await explorer.map_to_standard_concepts(
        query=query,
        confidence_threshold=0.4
    )
    
    if mappings:
        print(f"✅ Found {len(mappings)} high-confidence mappings")
        return [m['concept'] for m in mappings]
    
    # Step 4: Try alternative queries
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

# Use the workflow
async def main():
    standard_concepts = await find_standard_concepts_workflow("myocardial infarction")
    print(f"Found {len(standard_concepts)} standard concepts")

asyncio.run(main())
```

### Advanced Configuration

Configure exploration behavior for your specific needs:

```python
import asyncio
from athena_client.async_client import AthenaAsyncClient
from athena_client import create_concept_explorer

async def advanced_exploration():
    # Create async client and explorer
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)

    # Comprehensive exploration with all features
    results = await explorer.find_standard_concepts(
        query="diabetes",
        max_exploration_depth=3,        # How deep to explore relationships
        initial_seed_limit=15,          # Number of seed concepts to explore
        include_synonyms=True,          # Explore synonyms
        include_relationships=True,     # Explore relationships
        vocabulary_priority=[           # Preferred vocabularies
            'SNOMED', 
            'RxNorm', 
            'ICD10', 
            'LOINC'
        ]
    )

    # High-confidence mapping with specific vocabularies
    mappings = await explorer.map_to_standard_concepts(
        query="hypertension",
        target_vocabularies=['SNOMED', 'ICD10'],  # Only these vocabularies
        confidence_threshold=0.7                  # High confidence threshold
    )
asyncio.run(advanced_exploration())
```

### Use Cases

#### 1. Clinical Decision Support
```python
import asyncio
from athena_client.async_client import AthenaAsyncClient
from athena_client import create_concept_explorer

async def clinical_decision_support():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    # Find standard concepts for clinical conditions
    conditions = ["chest pain", "shortness of breath", "fever"]
    standard_concepts = {}

    for condition in conditions:
        mappings = await explorer.map_to_standard_concepts(
            condition, 
            target_vocabularies=['SNOMED'],
            confidence_threshold=0.6
        )
        if mappings:
            standard_concepts[condition] = mappings[0]['concept']
    
    return standard_concepts

asyncio.run(clinical_decision_support())
```

#### 2. Medication Mapping
```python
async def medication_mapping():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    # Map medication names to standard drug concepts
    medications = ["aspirin", "ibuprofen", "acetaminophen"]
    drug_concepts = {}

    for med in medications:
        mappings = await explorer.map_to_standard_concepts(
            med,
            target_vocabularies=['RxNorm'],
            confidence_threshold=0.5
        )
        if mappings:
            drug_concepts[med] = mappings[0]['concept']
    
    return drug_concepts

asyncio.run(medication_mapping())
```

#### 3. Cross-Vocabulary Mapping
```python
async def cross_vocabulary_mapping():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    # Map between different coding systems
    icd10_results = client.search_concepts("diabetes", vocabulary="ICD10")
    if icd10_results['content']:
        icd10_concept = icd10_results['content'][0]
        snomed_mappings = await explorer.map_to_standard_concepts(
            icd10_concept.name,
            target_vocabularies=['SNOMED'],
            confidence_threshold=0.7
        )
        return snomed_mappings
    
    return []

asyncio.run(cross_vocabulary_mapping())
```

### Best Practices

1. **Start with direct search** - It's faster and often sufficient
2. **Use appropriate confidence thresholds** - 0.5-0.7 for most use cases
3. **Specify target vocabularies** - Focus on relevant coding systems
4. **Explore relationships** - Useful for finding broader/narrower concepts
5. **Use synonyms** - Helps with alternative terminology
6. **Monitor and adjust timeout settings** - Especially for complex or large queries

### Performance Considerations

- **Exploration depth** affects performance - use 1-3 for most cases
- **Vocabulary filtering** reduces API calls and improves relevance
- **Confidence thresholds** help focus on high-quality matches
- **Caching** can be implemented for frequently used mappings

### Error Handling

The concept exploration functionality includes robust error handling:

```python
import asyncio
from athena_client.async_client import AthenaAsyncClient
from athena_client import create_concept_explorer

async def robust_exploration():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    try:
        mappings = await explorer.map_to_standard_concepts("diabetes")
        print(f"Found {len(mappings)} mappings")
    except Exception as e:
        print(f"Exploration failed: {e}")
        # Fall back to direct search
        results = client.search_concepts("diabetes")
        print(f"Direct search found {len(results['content'])} concepts")

asyncio.run(robust_exploration())
```

This concept exploration functionality helps ensure you can find the standard medical concepts you need, even when they don't appear directly in search results.

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

## Enhanced Large Query Handling

The athena-client provides intelligent handling for large queries with enhanced timeouts, progress tracking, and user-friendly error messages.

### Intelligent Timeout Management

Different operations use optimized timeouts based on query complexity:

```python
from athena_client import Athena

# Default timeouts are automatically adjusted based on query size
athena = Athena()

# Small queries: 30s timeout
results = athena.search("aspirin 325mg tablet")

# Large queries: 45s+ timeout (auto-adjusted)
results = athena.search("pain")  # Estimated 5000+ results

# Complex graphs: 60s+ timeout
graph = athena.graph(concept_id, depth=3, zoom_level=3)
```

### Progress Tracking for Long Operations

Large queries automatically show progress bars with ETA:

```python
# Progress tracking is enabled by default for large queries
results = athena.search("diabetes", size=100)
# Shows: Searching for 'diabetes': [██████████████████████████████] 100.0% (100/100) 2.3s

# Disable progress tracking if needed
results = athena.search("diabetes", show_progress=False)
```

### User-Friendly Warnings

The client warns about potentially large queries:

```python
results = athena.search("pain")
# Output:
# ⚠️  Large query detected: 'pain' (estimated 5,000+ results)
# 💡 Suggestions:
#    • Add more specific terms to narrow results
#    • Use domain or vocabulary filters
#    • Consider using smaller page sizes
#    • This query may take several minutes to complete
```

### Smart Pagination

Enhanced pagination with automatic validation and optimization:

```python
# Automatic page size validation
try:
    results = athena.search("aspirin", size=2000)  # Too large
except ValueError as e:
    print(e)  # "Page size 2000 exceeds maximum allowed size of 1000"

# Smart defaults based on query size
results = athena.search("pain")  # Uses smaller page size for large queries
```

### Enhanced Error Messages for Large Queries

Specific error messages for timeout and complexity issues:

```python
try:
    results = athena.search("very broad search term")
except APIError as e:
    print(e)
    # Output:
    # Search timeout: The query 'very broad search term' is taking too long to process.
    # Try:
    # • Using more specific search terms
    # • Adding domain or vocabulary filters
    # • Reducing the page size
    # • Breaking the query into smaller parts
```

### Configuration for Large Queries

Fine-tune large query behavior:

```python
from athena_client.settings import get_settings

settings = get_settings()

# Timeout configuration
settings.ATHENA_SEARCH_TIMEOUT_SECONDS = 60      # Search operations
settings.ATHENA_GRAPH_TIMEOUT_SECONDS = 90       # Graph operations
settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS = 60  # Relationship queries

# Pagination configuration
settings.ATHENA_DEFAULT_PAGE_SIZE = 50           # Default page size
settings.ATHENA_MAX_PAGE_SIZE = 1000             # Maximum page size
settings.ATHENA_LARGE_QUERY_THRESHOLD = 100      # Threshold for "large" queries

# Progress configuration
settings.ATHENA_SHOW_PROGRESS = True             # Enable progress tracking
settings.ATHENA_PROGRESS_UPDATE_INTERVAL = 2.0   # Update interval (seconds)
```

### Large Query Best Practices

```python
# 1. Use specific search terms
results = athena.search("acute myocardial infarction")  # Better than "heart attack"

# 2. Add filters to narrow results
results = athena.search("diabetes", domain="Condition", vocabulary="SNOMED")

# 3. Use smaller page sizes for large queries
results = athena.search("pain", size=20)  # Instead of 100

# 4. Enable progress tracking for visibility
results = athena.search("cancer", show_progress=True)

# 5. Monitor and adjust timeout settings
athena = Athena(timeout=60)  # Increase timeout for complex operations
```

### Large Query Features

✅ **Automatic timeout adjustment** based on query complexity  
✅ **Progress tracking** with ETA for long operations  
✅ **User-friendly warnings** for potentially large queries  
✅ **Smart pagination** with automatic validation  
✅ **Enhanced error messages** with specific suggestions
✅ **Memory-efficient processing** for large result sets
✅ **Configurable thresholds** for different query types

---

## Google BigQuery & OMOP Integration (Python 3.9 Only)

> **BigQuery support requires Python 3.9 due to upstream dependency constraints.**
> 
> - `pybigquery` (required for BigQuery) is only compatible with `sqlalchemy<1.5.0`.
> - The SDK will not work with BigQuery on Python 3.10+ or SQLAlchemy 2.x.

### Installation for BigQuery/OMOP

1. **Create a Python 3.9 virtual environment** (recommended):
   ```bash
   python3.9 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip setuptools
   ```
2. **Install the SDK with BigQuery extras:**
   ```bash
   pip install "athena-client[bigquery]"
   ```
   This will install compatible versions of `pybigquery` and `sqlalchemy`.

3. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```
   (Requires the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install))

4. **Set your environment variables:**
   ```bash
   export GCP_PROJECT_ID=your-gcp-project-id
   export BIGQUERY_DATASET=your_omop_dataset
   ```

5. **Run the example script:**
   ```bash
   python examples/bigquery_concept_set_demo.py
   ```
   The script will check your Python version and dependencies at runtime, and provide clear error messages if anything is missing.

### Example: Generating a Concept Set with BigQuery
See [`examples/bigquery_concept_set_demo.py`](examples/bigquery_concept_set_demo.py) for a full, robust example including:
- Dependency and Python version checks
- Google Cloud authentication guidance
- Usage of the Athena client with a BigQuery OMOP CDM

---

## Troubleshooting

- **Editable install fails with TOML or dependency errors?**
  - Ensure your `pyproject.toml` is valid and you are using Python 3.9.
  - Run `pip install --upgrade pip setuptools` before installing.
- **psycopg2-binary build errors (pg_config not found)?**
  - On macOS, run `brew install postgresql` to provide `pg_config`.
- **BigQuery install fails due to SQLAlchemy version conflict?**
  - Only `sqlalchemy>=1.4.0,<1.5.0` is supported for BigQuery. The SDK will install the correct version if you use the `[bigquery]` extra.
- **Python version errors?**
  - BigQuery support is only tested and supported on Python 3.9. Use `pyenv` or a `.python-version` file to enforce this if needed.

---
