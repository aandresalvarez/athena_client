# Athena Client: Complete Usage & Concept Exploration Guide

This guide is your comprehensive resource for using the `athena-client` Python SDK with the OHDSI Athena Concepts API. It covers installation, usage, CLI, advanced features, robust concept exploration, error handling, configuration, performance, and real-world best practices.

---

## 1. Installation & Environment

### Lightweight Installation (Recommended)

Install the core package with minimal dependencies:

```bash
pip install athena-client
```

This installs only 5 essential packages (~2MB) for basic API functionality.

### Full Installation

For all features including CLI, pandas support, and database integration:

```bash
pip install "athena-client[full]"
```

### Optional Features & Extras

Install only the features you need:

- **CLI Interface:**
  - `pip install "athena-client[cli]"` - Command-line interface
- **Data Analysis:**
  - `pip install "athena-client[pandas]"` - pandas DataFrame support
- **Format Support:**
  - `pip install "athena-client[yaml]"` - YAML format support
- **Authentication:**
  - `pip install "athena-client[crypto]"` - HMAC authentication
- **Database support:**
  - PostgreSQL: `pip install "athena-client[postgres]"`
  - BigQuery: `pip install "athena-client[bigquery]"` (Python 3.9 only)
  - All databases: `pip install "athena-client[db]"`
- **Async support:**
  - `pip install "athena-client[async]"` - Async client support

> **BigQuery users:** Use Python 3.9 and `sqlalchemy<1.5.0` for compatibility.

#### Reducing Dependency Conflicts
- Install only the extras you need.
- For BigQuery, use Python 3.9 and compatible SQLAlchemy.
- For maximum compatibility, use the latest Python and dependencies.

---

## 2. Advanced Query DSL

The Query DSL provides a powerful way to build complex search queries using Python operators.

### Basic Query Types

```python
from athena_client.query import Q

# Term search - searches across multiple fields with different weights
q1 = Q.term("diabetes")

# Phrase search - exact phrase matching
q2 = Q.phrase("heart attack")

# Exact match - precise matching with quotes
q3 = Q.exact('"Myocardial Infarction"')

# Wildcard search - pattern matching
q4 = Q.wildcard("aspir*")  # Matches aspirin, aspiring, etc.
```

### Complex Query Combinations

```python
# AND operator - both terms must match
diabetes_and_type2 = Q.term("diabetes") & Q.term("type 2")

# OR operator - either term can match
heart_or_cardiac = Q.term("heart") | Q.term("cardiac")

# NOT operator - exclude terms
pain_not_chronic = -Q.term("chronic")

# Complex nested queries
complex_query = (
    (Q.term("diabetes") & Q.term("type 2")) | 
    (Q.term("T2DM") & -Q.term("gestational"))
)
```

### Fuzzy Matching

```python
# Fuzzy matching with custom ratio (0.0 - 1.0)
fuzzy_aspirin = Q.term("aspirin").fuzzy(0.8)

# Combine fuzzy with other operators
fuzzy_diabetes = Q.term("diabetes").fuzzy(0.7) & Q.term("type 2")
```

### Using Queries in Search

```python
# Use Query DSL objects directly in search
results = athena.search(complex_query)

# Combine with other search parameters
results = athena.search(
    complex_query,
    page=0,
    size=50,
    domain="Condition"
)
```

### Query DSL Internals

The Query DSL converts to Athena API boosts:

```python
# Get the underlying query structure
boosts = complex_query.to_boosts()
print(boosts)

# Convert to string representation
query_string = str(complex_query)
print(query_string)
```

---

## 3. Advanced SearchResult Features

The `SearchResult` class provides rich functionality beyond basic result access.

### Pagination Methods

```python
# Navigate through pages
results = athena.search("aspirin", size=10)

# Get next page
next_page = results.next_page()
if next_page:
    print(f"Next page has {len(next_page.all())} results")

# Get previous page
prev_page = results.previous_page()
if prev_page:
    print(f"Previous page has {len(prev_page.all())} results")
```

### Pagination Properties

```python
# Get pagination information
print(f"Total elements: {results.total_elements}")
print(f"Total pages: {results.total_pages}")
print(f"Current page: {results.current_page}")
print(f"Page size: {results.page_size}")

# Check pagination state
print(f"Is first page: {results._response.first}")
print(f"Is last page: {results._response.last}")
```

### Facets and Metadata

```python
# Access search facets if available
facets = results.facets
if facets:
    print("Available facets:")
    for facet_name, facet_data in facets.items():
        print(f"  {facet_name}: {len(facet_data)} values")
```

### Iteration and Indexing

```python
# Iterate over concepts
for concept in results:
    print(f"Concept: {concept.name} ({concept.vocabulary})")

# Index access
first_concept = results[0]
last_concept = results[-1]

# Length
print(f"Number of concepts on this page: {len(results)}")
```

### Advanced Result Processing

```python
# Filter concepts by standard status
standard_concepts = [c for c in results.all() if c.standardConcept == "Standard"]

# Group by vocabulary
from collections import defaultdict
vocab_groups = defaultdict(list)
for concept in results.all():
    vocab_groups[concept.vocabulary].append(concept)

# Sort by relevance score
sorted_concepts = sorted(results.all(), key=lambda c: c.score or 0, reverse=True)
```

---

## 4. Progress Tracking and Large Query Handling

The library provides sophisticated progress tracking and large query handling capabilities.

### Automatic Progress Tracking

```python
# Large queries automatically show progress
results = athena.search("pain")  # Shows progress bar for large result sets

# Custom progress tracking
from athena_client.utils import progress_context, ProgressTracker

# Using context manager
with progress_context(total=1000, description="Searching concepts..."):
    results = athena.search("large query")

# Using ProgressTracker directly
tracker = ProgressTracker(
    total=500,
    description="Processing concepts",
    show_progress=True,
    update_interval=1.0
)
tracker.start()
# ... process items ...
tracker.update(100)
tracker.complete()
```

### Query Size Estimation

```python
from athena_client.utils import estimate_query_size, format_large_query_warning

# Estimate query size
estimated_size = estimate_query_size("diabetes")
print(f"Estimated results: {estimated_size}")

# Get warnings for large queries
warning = format_large_query_warning("pain", estimated_size=5000, requested_size=100)
if warning:
    print(warning)
```

### Large Query Configuration

```python
from athena_client.settings import get_settings

settings = get_settings()

# Configure large query handling
settings.ATHENA_LARGE_QUERY_THRESHOLD = 200  # Show progress for >200 results
settings.ATHENA_SHOW_PROGRESS = True
settings.ATHENA_PROGRESS_UPDATE_INTERVAL = 2.0

# Configure timeouts for different operations
settings.ATHENA_SEARCH_TIMEOUT_SECONDS = 60
settings.ATHENA_GRAPH_TIMEOUT_SECONDS = 90
settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS = 60
```

### Memory-Efficient Processing

```python
# Process large result sets efficiently
results = athena.search("large query", size=1000)

# Process in chunks
chunk_size = 100
for i in range(0, len(results), chunk_size):
    chunk = results.all()[i:i + chunk_size]
    # Process chunk
    print(f"Processed chunk {i//chunk_size + 1}")
```

---

## 5. Command-Line Interface (CLI)

The library provides sophisticated progress tracking and large query handling capabilities.

### Automatic Progress Tracking

```python
# Large queries automatically show progress
results = athena.search("pain")  # Shows progress bar for large result sets

# Custom progress tracking
from athena_client.utils import progress_context, ProgressTracker

# Using context manager
with progress_context(total=1000, description="Searching concepts..."):
    results = athena.search("large query")

# Using ProgressTracker directly
tracker = ProgressTracker(
    total=500,
    description="Processing concepts",
    show_progress=True,
    update_interval=1.0
)
tracker.start()
# ... process items ...
tracker.update(100)
tracker.complete()
```

### Query Size Estimation

```python
from athena_client.utils import estimate_query_size, format_large_query_warning

# Estimate query size
estimated_size = estimate_query_size("diabetes")
print(f"Estimated results: {estimated_size}")

# Get warnings for large queries
warning = format_large_query_warning("pain", estimated_size=5000, requested_size=100)
if warning:
    print(warning)
```

### Large Query Configuration

```python
from athena_client.settings import get_settings

settings = get_settings()

# Configure large query handling
settings.ATHENA_LARGE_QUERY_THRESHOLD = 200  # Show progress for >200 results
settings.ATHENA_SHOW_PROGRESS = True
settings.ATHENA_PROGRESS_UPDATE_INTERVAL = 2.0

# Configure timeouts for different operations
settings.ATHENA_SEARCH_TIMEOUT_SECONDS = 60
settings.ATHENA_GRAPH_TIMEOUT_SECONDS = 90
settings.ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS = 60
```

### Memory-Efficient Processing

```python
# Process large result sets efficiently
results = athena.search("large query", size=1000)

# Process in chunks
chunk_size = 100
for i in range(0, len(results), chunk_size):
    chunk = results.all()[i:i + chunk_size]
    # Process chunk
    print(f"Processed chunk {i//chunk_size + 1}")
```

---

## 6. Advanced CLI Usage

The CLI provides powerful filtering and output options for command-line usage.

### Advanced Search Options

```bash
# Fuzzy matching
athena search "asprin" --fuzzy

# Domain and vocabulary filtering
athena search "diabetes" --domain Condition --vocabulary SNOMED

# Pagination control
athena search "aspirin" --page-size 50 --page 2

# Limit results
athena search "aspirin" --limit 10

# Combine multiple filters
athena search "diabetes" --domain Condition --vocabulary SNOMED --limit 5 --fuzzy
```

### Advanced Relationship Options

```bash
# Filter by relationship type
athena relationships 1127433 --relationship-id "Maps to"

# Only standard concepts
athena relationships 1127433 --only-standard

# All relationships (default)
athena relationships 1127433 --all
```

### Advanced Graph Options

```bash
# Custom depth and zoom
athena graph 1127433 --depth 3 --zoom-level 4

# Different output formats
athena graph 1127433 --depth 2 --output json
athena graph 1127433 --depth 2 --output csv
```

### Output Format Control

```bash
# JSON output with pretty formatting
athena search "aspirin" --output json | jq '.'

# CSV output for spreadsheet import
athena search "aspirin" --output csv > aspirin_concepts.csv

# YAML output (requires yaml extra)
athena search "aspirin" --output yaml > aspirin_concepts.yaml

# Table output (default)
athena search "aspirin" --output table

# Pretty output with colors
athena search "aspirin" --output pretty
```

### File Export Examples

```bash
# Export to JSON (remove warning lines)
athena search "aspirin" --output json | tail -n +2 > aspirin.json

# Export to CSV with specific fields
athena search "aspirin" --output csv | tail -n +2 > aspirin.csv

# Export multiple queries
for query in "aspirin" "ibuprofen" "acetaminophen"; do
    athena search "$query" --output json | tail -n +2 > "${query}_concepts.json"
done
```

---

## 7. Advanced Configuration Management

The library provides comprehensive configuration management for different environments.

### Settings Management

```python
from athena_client.settings import get_settings, clear_settings_cache, reload_settings

# Get current settings
settings = get_settings()

# Modify settings
settings.ATHENA_TIMEOUT_SECONDS = 60
settings.ATHENA_MAX_RETRIES = 5
settings.ATHENA_SHOW_PROGRESS = True

# Clear cache and reload from environment
clear_settings_cache()
new_settings = reload_settings()
```

### Environment Variable Configuration

```bash
# Core settings
export ATHENA_BASE_URL="https://your-server.com/api/v1"
export ATHENA_TOKEN="your-token"
export ATHENA_TIMEOUT_SECONDS="60"
export ATHENA_MAX_RETRIES="5"

# Advanced settings
export ATHENA_SHOW_PROGRESS="true"
export ATHENA_PROGRESS_UPDATE_INTERVAL="2.0"
export ATHENA_LARGE_QUERY_THRESHOLD="100"
export ATHENA_DEFAULT_PAGE_SIZE="50"
export ATHENA_MAX_PAGE_SIZE="1000"

# Operation-specific timeouts
export ATHENA_SEARCH_TIMEOUT_SECONDS="60"
export ATHENA_GRAPH_TIMEOUT_SECONDS="90"
export ATHENA_RELATIONSHIPS_TIMEOUT_SECONDS="60"
```

### Configuration Precedence

```python
# 1. Direct parameters (highest priority)
athena = Athena(
    base_url="https://custom-server.com/api/v1",
    timeout=30,
    max_retries=3
)

# 2. Environment variables
# ATHENA_BASE_URL=https://env-server.com/api/v1

# 3. Default values (lowest priority)
# base_url="https://athena.ohdsi.org/api/v1"
```

### Configuration for Different Environments

```python
# Development environment
dev_athena = Athena(
    base_url="http://localhost:8080/api/v1",
    enable_throttling=False,
    timeout=10,
    max_retries=1
)

# Production environment
prod_athena = Athena(
    base_url="https://production-server.com/api/v1",
    enable_throttling=True,
    timeout=60,
    max_retries=5
)

# High-latency network
remote_athena = Athena(
    base_url="https://remote-server.com/api/v1",
    timeout=120,
    max_retries=7,
    enable_throttling=True
)
```

---

## 8. Advanced Error Handling and Retry Logic

The library provides sophisticated error handling with detailed error information and retry control.

### Error Types and Handling

```python
from athena_client.exceptions import (
    NetworkError, TimeoutError, ClientError, ServerError,
    AuthenticationError, RateLimitError, ValidationError, APIError
)

try:
    results = athena.search("aspirin")
except NetworkError as e:
    print(f"Network issue: {e}")
    print(f"URL that failed: {e.url}")
    print(f"Troubleshooting: {e.troubleshooting}")
except TimeoutError as e:
    print(f"Timeout after {e.timeout} seconds")
except RateLimitError as e:
    print(f"Rate limited: {e}")
    print(f"Retry after: {e.retry_after}")
except APIError as e:
    print(f"API error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Troubleshooting: {e.troubleshooting}")
```

### Advanced Retry Configuration

```python
# Global retry configuration
athena = Athena(
    max_retries=5,
    retry_delay=2.0,
    enable_throttling=True,
    throttle_delay_range=(0.1, 0.5)
)

# Per-call retry configuration
results = athena.search(
    "aspirin",
    auto_retry=True,
    max_retries=3,
    retry_delay=1.0,
    show_progress=True
)

# Disable retry for specific calls
results = athena.search("aspirin", auto_retry=False)
```

### Custom Error Recovery

```python
def search_with_fallback(query, fallback_queries=None):
    """Search with fallback queries if the main query fails."""
    try:
        return athena.search(query)
    except APIError as e:
        if fallback_queries:
            for fallback in fallback_queries:
                try:
                    print(f"Trying fallback query: {fallback}")
                    return athena.search(fallback)
                except APIError:
                    continue
        raise e

# Usage
results = search_with_fallback(
    "myocardial infarction",
    fallback_queries=["heart attack", "MI", "cardiac infarction"]
)
```

### Error Analysis and Debugging

```python
import logging
from athena_client.utils import configure_logging

# Configure detailed logging
configure_logging(level=logging.DEBUG)

# This will show detailed HTTP requests and responses
results = athena.search("aspirin")
```

---

## 9. Advanced Concept Exploration

The ConceptExplorer provides powerful async features for discovering standard concepts and building concept mappings.

### Basic Concept Exploration

```python
import asyncio
from athena_client.concept_explorer import create_concept_explorer

async def basic_exploration():
    explorer = create_concept_explorer(athena)
    
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
    
    return results

asyncio.run(basic_exploration())
```

### Advanced Concept Mapping

```python
async def advanced_mapping():
    explorer = create_concept_explorer(athena)
    
    # Map concepts with confidence scores
    mappings = await explorer.map_to_standard_concepts(
        query="migraine",
        target_vocabularies=['SNOMED', 'RxNorm'],
        confidence_threshold=0.5
    )
    
    for mapping in mappings:
        concept = mapping['concept']
        confidence = mapping['confidence']
        path = mapping['exploration_path']
        source = mapping['source_category']
        
        print(f"Concept: {concept.name}")
        print(f"Vocabulary: {concept.vocabulary}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Discovery path: {path}")
        print(f"Source: {source}\n")
    
    return mappings

asyncio.run(advanced_mapping())
```

### Alternative Query Suggestions

```python
async def get_suggestions():
    explorer = create_concept_explorer(athena)
    
    suggestions = await explorer.suggest_alternative_queries(
        query="heart attack", 
        max_suggestions=8
    )
    
    print("Alternative suggestions:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    return suggestions

asyncio.run(get_suggestions())
```

### Concept Hierarchy Exploration

```python
async def explore_hierarchy():
    explorer = create_concept_explorer(athena)
    
    hierarchy = await explorer.get_concept_hierarchy(
        concept_id=12345, 
        max_depth=3
    )
    
    print(f"Root concept: {hierarchy['root_concept'].name}")
    print(f"Parent relationships: {len(hierarchy['parents'])}")
    print(f"Child relationships: {len(hierarchy['children'])}")
    print(f"Sibling relationships: {len(hierarchy['siblings'])}")
    
    return hierarchy

asyncio.run(explore_hierarchy())
```

### Comprehensive Exploration Workflow

```python
async def comprehensive_workflow(query):
    """Complete workflow for finding standard concepts."""
    explorer = create_concept_explorer(athena)
    
    # Step 1: Direct search
    direct_results = await athena.search(query, size=10)
    direct_standard = [c for c in direct_results.all() if c.standardConcept == "Standard"]
    
    if direct_standard:
        print(f"✅ Found {len(direct_standard)} standard concepts directly")
        return direct_standard
    
    # Step 2: Exploration
    print("🔍 Exploring for standard concepts...")
    exploration_results = await explorer.find_standard_concepts(
        query=query,
        max_exploration_depth=3,
        initial_seed_limit=10,
        include_synonyms=True,
        include_relationships=True
    )
    
    # Step 3: Mapping with confidence
    mappings = await explorer.map_to_standard_concepts(
        query=query,
        confidence_threshold=0.4
    )
    
    if mappings:
        print(f"✅ Found {len(mappings)} high-confidence mappings")
        return [m['concept'] for m in mappings]
    
    # Step 4: Alternative queries
    print("💡 Trying alternative queries...")
    suggestions = await explorer.suggest_alternative_queries(query, max_suggestions=5)
    
    for suggestion in suggestions:
        test_results = await athena.search(suggestion, size=5)
        standard_found = [c for c in test_results.all() if c.standardConcept == "Standard"]
        if standard_found:
            print(f"✅ Found standard concepts with suggestion: '{suggestion}'")
            return standard_found
    
    print("❌ No standard concepts found")
    return []

# Usage
asyncio.run(comprehensive_workflow("myocardial infarction"))
```

### Performance Optimization

```python
async def optimized_exploration():
    """Optimized exploration with performance considerations."""
    explorer = create_concept_explorer(athena)
    
    # Use limits to control resource usage
    results = await explorer.find_standard_concepts(
        query="diabetes",
        max_exploration_depth=2,  # Limit depth for performance
        initial_seed_limit=5,     # Limit initial seeds
        max_total_concepts=50,    # Limit total concepts
        max_api_calls=30,         # Limit API calls
        max_time_seconds=20,      # Limit execution time
        vocabulary_priority=['SNOMED', 'RxNorm']  # Focus on relevant vocabularies
    )
    
    return results

asyncio.run(optimized_exploration())
```

---

## 10. Advanced Database Integration

The library provides experimental database integration for concept set validation and generation.

### Database Connector Setup

```python
from athena_client.db.sqlalchemy_connector import SQLAlchemyConnector

# PostgreSQL connector
postgres_connector = SQLAlchemyConnector.from_connection_string(
    "postgresql://user:pass@localhost/omop_cdm"
)

# BigQuery connector (Python 3.9 only)
bigquery_connector = SQLAlchemyConnector.from_connection_string(
    "bigquery://project/dataset"
)

# Set connector on client
athena.set_database_connector(postgres_connector)
```

### Local Concept Validation

```python
# Validate concept IDs against local database
concept_ids = [1127433, 1112807, 999999999]
valid_concepts = athena.validate_local_concepts(concept_ids)

print(f"Valid concepts: {valid_concepts}")
print(f"Invalid concepts: {set(concept_ids) - set(valid_concepts)}")
```

### Advanced Concept Set Generation

```python
async def advanced_concept_set_generation():
    """Generate concept sets with advanced options."""
    
    # Strict strategy - only use concepts found in local database
    strict_set = await athena.generate_concept_set(
        query="Type 2 Diabetes",
        db_connection_string="postgresql://user:pass@localhost/omop_cdm",
        strategy="strict",
        include_descendants=False,
        confidence_threshold=0.8
    )
    
    # Fallback strategy - use broader search if strict fails
    fallback_set = await athena.generate_concept_set(
        query="Type 2 Diabetes",
        db_connection_string="postgresql://user:pass@localhost/omop_cdm",
        strategy="fallback",
        include_descendants=True,
        confidence_threshold=0.6
    )
    
    return strict_set, fallback_set

asyncio.run(advanced_concept_set_generation())
```

### Database-Specific Features

```python
# PostgreSQL-specific features
if hasattr(postgres_connector, 'get_descendants'):
    descendants = postgres_connector.get_descendants([1127433])
    print(f"Descendants: {descendants}")

# Standard concept mapping
if hasattr(postgres_connector, 'get_standard_mapping'):
    mappings = postgres_connector.get_standard_mapping([1127433])
    print(f"Standard mappings: {mappings}")
```

---

## 11. Utility Functions and Advanced Features

The library provides various utility functions for advanced usage scenarios.

### Logging Configuration

```python
from athena_client.utils import configure_logging
import logging

# Configure detailed logging
configure_logging(level=logging.DEBUG)

# Configure specific logger
configure_logging(level=logging.INFO, logger_name="athena_client.http")
```

### Timeout Management

```python
from athena_client.utils import get_operation_timeout

# Get appropriate timeouts for different operations
search_timeout = get_operation_timeout("search", query_size=1000)
graph_timeout = get_operation_timeout("graph", query_size=500)
relationship_timeout = get_operation_timeout("relationships", query_size=200)

print(f"Search timeout: {search_timeout}s")
print(f"Graph timeout: {graph_timeout}s")
print(f"Relationship timeout: {relationship_timeout}s")
```

### Query Analysis

```python
from athena_client.utils import estimate_query_size, format_large_query_warning

# Analyze query complexity
queries = ["aspirin", "diabetes", "pain", "heart attack"]
for query in queries:
    estimated_size = estimate_query_size(query)
    warning = format_large_query_warning(query, estimated_size)
    print(f"Query: {query}")
    print(f"  Estimated size: {estimated_size}")
    print(f"  Warning: {warning if warning else 'None'}")
```

### Progress Tracking Utilities

```python
from athena_client.utils import ProgressTracker, progress_context

# Custom progress tracking
def process_concepts(concepts):
    with progress_context(
        total=len(concepts),
        description="Processing concepts",
        show_progress=True,
        update_interval=1.0
    ) as tracker:
        for concept in concepts:
            # Process concept
            tracker.update(1)

# Manual progress tracking
tracker = ProgressTracker(
    total=100,
    description="Custom operation",
    show_progress=True,
    update_interval=0.5
)
tracker.start()
# ... perform operations ...
tracker.update(50)
tracker.complete()
```

---

## 12. Real-World Use Cases and Best Practices

### Clinical Decision Support

```python
async def clinical_decision_support():
    """Map symptoms to standard concepts for clinical decision support."""
    explorer = create_concept_explorer(athena)
    
    symptoms = ["chest pain", "shortness of breath", "fever", "nausea"]
    standard_concepts = {}
    
    for symptom in symptoms:
        mappings = await explorer.map_to_standard_concepts(
            symptom, 
            target_vocabularies=['SNOMED'], 
            confidence_threshold=0.6
        )
        if mappings:
            standard_concepts[symptom] = mappings[0]['concept']
    
    return standard_concepts

asyncio.run(clinical_decision_support())
```

### Medication Mapping

```python
async def medication_mapping():
    """Map drug names to RxNorm standard concepts."""
    explorer = create_concept_explorer(athena)
    
    medications = ["aspirin", "ibuprofen", "acetaminophen", "metformin"]
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

### Cross-Vocabulary Mapping

```python
async def cross_vocabulary_mapping():
    """Map concepts between different vocabularies."""
    explorer = create_concept_explorer(athena)
    
    # Start with ICD-10 concept
    icd10_results = await athena.search("diabetes", vocabulary="ICD10")
    
    if icd10_results.all():
        icd10_concept = icd10_results.all()[0]
        
        # Map to SNOMED
        snomed_mappings = await explorer.map_to_standard_concepts(
            icd10_concept.name, 
            target_vocabularies=['SNOMED'], 
            confidence_threshold=0.7
        )
        
        # Map to RxNorm for medications
        rxnorm_mappings = await explorer.map_to_standard_concepts(
            icd10_concept.name, 
            target_vocabularies=['RxNorm'], 
            confidence_threshold=0.7
        )
        
        return {
            'icd10': icd10_concept,
            'snomed': snomed_mappings,
            'rxnorm': rxnorm_mappings
        }
    
    return {}

asyncio.run(cross_vocabulary_mapping())
```

### Data Quality Validation

```python
async def validate_concept_set(concept_ids, db_connection_string):
    """Validate a concept set against local OMOP database."""
    
    # Generate concept set with validation
    concept_set = await athena.generate_concept_set(
        query="Type 2 Diabetes",
        db_connection_string=db_connection_string,
        strategy="strict",
        include_descendants=True,
        confidence_threshold=0.7
    )
    
    # Check validation results
    metadata = concept_set.get("metadata", {})
    if metadata.get("status") == "SUCCESS":
        print(f"✅ Concept set generated successfully")
        print(f"   Concepts: {len(concept_set.get('concept_ids', []))}")
        print(f"   Strategy used: {metadata.get('strategy_used')}")
        
        # Check warnings
        for warning in metadata.get("warnings", []):
            print(f"   ⚠️  Warning: {warning}")
    else:
        print(f"❌ Concept set generation failed: {metadata.get('reason')}")
    
    return concept_set

# Usage
asyncio.run(validate_concept_set(
    [1127433, 1112807], 
    "postgresql://user:pass@localhost/omop_cdm"
))
```

### Performance Optimization Best Practices

```python
# 1. Use appropriate timeouts
athena = Athena(
    timeout=60,
    max_retries=3,
    enable_throttling=True
)

# 2. Use pagination for large result sets
results = athena.search("large query", size=50, page=0)

# 3. Enable progress tracking for long operations
results = athena.search("complex query", show_progress=True)

# 4. Use vocabulary filtering to reduce API calls
results = athena.search("diabetes", vocabulary="SNOMED")

# 5. Implement caching for frequently used queries
import functools

@functools.lru_cache(maxsize=100)
def cached_search(query):
    return athena.search(query)

# 6. Use async operations for multiple queries
async def batch_search(queries):
    tasks = [athena.search(query) for query in queries]
    return await asyncio.gather(*tasks)
```

### Error Recovery Best Practices

```python
def robust_search(query, max_retries=3):
    """Robust search with multiple fallback strategies."""
    
    # Try original query
    try:
        return athena.search(query)
    except Exception as e:
        print(f"Original query failed: {e}")
    
    # Try fuzzy search
    try:
        return athena.search(query, fuzzy=True)
    except Exception as e:
        print(f"Fuzzy search failed: {e}")
    
    # Try broader search
    try:
        broader_terms = query.split()[:2]  # Use first two words
        broader_query = " ".join(broader_terms)
        return athena.search(broader_query)
    except Exception as e:
        print(f"Broader search failed: {e}")
    
    # Return empty results
    return None

# Usage
results = robust_search("complex medical term")
```

---

## 13. Troubleshooting & Compatibility

### Common Issues and Solutions

#### Installation Issues

```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Install with specific Python version for BigQuery
pyenv local 3.9.18
pip install "athena-client[bigquery]"

# Install PostgreSQL development tools (macOS)
brew install postgresql
```

#### Dependency Conflicts

```bash
# Use virtual environment
python -m venv athena_env
source athena_env/bin/activate  # On Windows: athena_env\Scripts\activate

# Install with specific versions
pip install "athena-client[full]"
```

#### Network and Connection Issues

```python
# Test connection
try:
    athena = Athena()
    results = athena.search("test")
    print("✅ Connection successful")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    
    # Try with different configuration
    athena = Athena(
        timeout=120,
        max_retries=5,
        enable_throttling=False
    )
```

### Version Compatibility Matrix

| Component | Minimum | Maximum | Notes |
|-----------|---------|---------|-------|
| Python | 3.9 | 3.12 | BigQuery requires 3.9 |
| SQLAlchemy | 1.4.0 | 2.x | BigQuery needs <1.5.0 |
| pandas | 1.3.0 | 2.x | |
| pydantic | 2.0.0 | 3.x | |
| httpx | 0.18.0 | Latest | |
| cryptography | 36.0.0 | Latest | |

### Performance Tuning

```python
# Optimize for high-throughput scenarios
athena = Athena(
    timeout=30,
    max_retries=2,
    enable_throttling=True,
    throttle_delay_range=(0.05, 0.1)  # Faster throttling
)

# Optimize for reliability
athena = Athena(
    timeout=120,
    max_retries=5,
    enable_throttling=True,
    throttle_delay_range=(0.2, 0.5)  # Slower, more reliable
)
```

---

## 14. Advanced Examples and Demos

### Complete Workflow Example

```python
import asyncio
from athena_client import Athena
from athena_client.concept_explorer import create_concept_explorer

async def complete_workflow():
    """Complete workflow from search to concept set generation."""
    
    # Initialize client
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    # Step 1: Search for concepts
    print("🔍 Searching for concepts...")
    results = await athena.search("Type 2 Diabetes", size=20)
    
    # Step 2: Analyze results
    print(f"Found {len(results.all())} concepts")
    standard_concepts = [c for c in results.all() if c.standardConcept == "Standard"]
    print(f"Standard concepts: {len(standard_concepts)}")
    
    # Step 3: Explore relationships
    if results.all():
        concept_id = results.all()[0].id
        print(f"🔗 Exploring relationships for concept {concept_id}...")
        relationships = await athena.relationships(concept_id)
        print(f"Found {relationships.count} relationships")
        
        # Step 4: Get concept graph
        print(f"🕸️  Building concept graph...")
        graph = await athena.graph(concept_id, depth=2, zoom_level=2)
        print(f"Graph has {len(graph.terms)} terms and {len(graph.links)} links")
        
        # Step 5: Advanced exploration
        print(f"🔬 Advanced concept exploration...")
        exploration_results = await explorer.find_standard_concepts(
            query="Type 2 Diabetes",
            max_exploration_depth=2,
            vocabulary_priority=['SNOMED', 'RxNorm']
        )
        
        print(f"Exploration found:")
        print(f"  - Direct matches: {len(exploration_results['direct_matches'])}")
        print(f"  - Synonym matches: {len(exploration_results['synonym_matches'])}")
        print(f"  - Relationship matches: {len(exploration_results['relationship_matches'])}")
        
        # Step 6: Generate concept set (if database available)
        try:
            print(f"📊 Generating concept set...")
            concept_set = await athena.generate_concept_set(
                query="Type 2 Diabetes",
                db_connection_string="postgresql://user:pass@localhost/omop_cdm",
                strategy="fallback"
            )
            
            metadata = concept_set.get("metadata", {})
            if metadata.get("status") == "SUCCESS":
                print(f"✅ Concept set generated with {len(concept_set.get('concept_ids', []))} concepts")
            else:
                print(f"❌ Concept set generation failed: {metadata.get('reason')}")
                
        except Exception as e:
            print(f"⚠️  Concept set generation skipped: {e}")
    
    print("🎉 Workflow completed!")

# Run the complete workflow
asyncio.run(complete_workflow())
```

### Batch Processing Example

```python
async def batch_process_concepts(queries):
    """Process multiple queries efficiently."""
    
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    results = {}
    
    for query in queries:
        print(f"Processing: {query}")
        
        try:
            # Search
            search_results = await athena.search(query, size=10)
            
            # Explore
            exploration = await explorer.find_standard_concepts(
                query=query,
                max_exploration_depth=1,
                max_total_concepts=20
            )
            
            # Map to standard concepts
            mappings = await explorer.map_to_standard_concepts(
                query=query,
                confidence_threshold=0.5
            )
            
            results[query] = {
                'search': search_results.all(),
                'exploration': exploration,
                'mappings': mappings
            }
            
        except Exception as e:
            print(f"Error processing {query}: {e}")
            results[query] = {'error': str(e)}
    
    return results

# Usage
queries = ["aspirin", "diabetes", "hypertension", "cancer"]
results = asyncio.run(batch_process_concepts(queries))
```

---

For more details, see the [README](./README.md) or the official documentation. This guide is designed to be your one-stop resource for robust, production-ready concept exploration and Athena API integration.
