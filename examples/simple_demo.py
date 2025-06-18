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
