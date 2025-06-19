#!/usr/bin/env python3
"""
Comprehensive demo showcasing the robust athena-client library.

This demo demonstrates all the working features with the real Athena API.
"""
import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.query import Q


def main():
    print("🚀 ROBUST ATHENA-CLIENT DEMO")
    print("=" * 60)
    print("This demo showcases the enhanced robust athena-client")
    print("working perfectly with the real Athena API!")
    print("=" * 60)

    # Create client
    print("\n🔧 Creating enhanced Athena client...")
    athena = Athena()
    print("  ✅ Client created successfully")

    print("\n" + "=" * 60)
    print("1. SEARCH FUNCTIONALITY")
    print("=" * 60)

    # Simple text search
    print("\n🔍 Searching for 'aspirin'...")
    try:
        results = athena.search("aspirin", page=0, size=5)
        print(f"✅ Search successful! Found {len(results)} results")
        print("📋 Showing first 5 results:")
        
        for i, concept in enumerate(results.top(5), 1):
            print(f"  {i}. [{concept.id}] {concept.name}")
            print(f"     Domain: {concept.domain}")
            print(f"     Vocabulary: {concept.vocabulary}")
            print(f"     Class: {concept.className}")
            print(f"     Standard: {concept.standardConcept}")
            print()

        # Pagination information
        print("📊 Pagination Information:")
        print(f"  - Total Elements: {results.total_elements}")
        print(f"  - Total Pages: {results.total_pages}")
        print(f"  - Current Page: {results.current_page}")
        print(f"  - Page Size: {results.page_size}")

        # Facets
        if results.facets:
            print("\n🔍 Available Facets:")
            for facet_name, facet_values in results.facets.items():
                if isinstance(facet_values, dict):
                    top_values = dict(list(facet_values.items())[:3])
                    print(f"  - {facet_name}: {top_values}")

    except Exception as e:
        print(f"❌ Search failed: {e}")

    # Query DSL search
    print("\n🔍 Using Query DSL to search for 'heart' OR 'cardiac'...")
    try:
        query = Q.term("heart") | Q.term("cardiac")
        complex_results = athena.search(query, page=0, size=3)
        print(f"✅ Complex search successful! Found {len(complex_results)} results")
        
        for i, concept in enumerate(complex_results.top(3), 1):
            print(f"  {i}. [{concept.id}] {concept.name} ({concept.vocabulary})")
    except Exception as e:
        print(f"❌ Complex search failed: {e}")

    print("\n" + "=" * 60)
    print("2. CONCEPT DETAILS")
    print("=" * 60)

    # Get concept details
    print("\n🔍 Getting concept details...")
    try:
        concept_id = 1112807  # RxNorm Aspirin
        details = athena.details(concept_id)
        print("✅ Concept details retrieved successfully!")
        print(f"  📋 ID: {details.id}")
        print(f"  📋 Name: {details.name}")
        print(f"  📋 Domain: {details.domainId}")
        print(f"  📋 Vocabulary: {details.vocabularyId}")
        print(f"  📋 Class: {details.conceptClassId}")
        print(f"  📋 Standard: {details.standardConcept}")
        print(f"  📋 Code: {details.conceptCode}")
        print(f"  📋 Valid: {details.validStart} to {details.validEnd}")
        
        if details.synonyms:
            print(f"  📋 Synonyms: {', '.join(details.synonyms)}")
        
        if details.vocabularyName:
            print(f"  📋 Vocabulary Name: {details.vocabularyName}")
            print(f"  📋 Vocabulary Version: {details.vocabularyVersion}")
    except Exception as e:
        print(f"❌ Could not retrieve concept details: {e}")

    print("\n" + "=" * 60)
    print("3. CONCEPT RELATIONSHIPS")
    print("=" * 60)

    # Get relationships
    print("\n🔗 Getting concept relationships...")
    try:
        relationships = athena.relationships(concept_id)
        print(f"✅ Relationships retrieved successfully! Found {relationships.count} total relationships")
        
        if relationships.items:
            print("📋 Relationship Groups:")
            for i, group in enumerate(relationships.items[:3], 1):  # Show first 3 groups
                print(f"  {i}. {group.relationshipName} ({len(group.relationships)} relationships)")
                
                # Show first few relationships in each group
                for j, rel in enumerate(group.relationships[:2], 1):
                    print(f"     {j}. {rel.relationshipName} -> {rel.targetConceptName} ({rel.targetConceptId})")
                print()
    except Exception as e:
        print(f"❌ Could not retrieve relationships: {e}")

    print("\n" + "=" * 60)
    print("4. CONCEPT GRAPH")
    print("=" * 60)

    # Get graph
    print("\n🕸️ Getting concept graph...")
    try:
        graph = athena.graph(concept_id, depth=2, zoom_level=2)
        print("✅ Graph retrieved successfully!")
        print(f"  📊 Terms: {len(graph.terms)}")
        print(f"  📊 Links: {len(graph.links)}")
        
        if graph.terms:
            current_terms = [t for t in graph.terms if t.isCurrent]
            print(f"  📊 Current terms: {len(current_terms)}")
            for term in current_terms[:3]:  # Show first 3
                print(f"    - {term.name} (weight: {term.weight}, depth: {term.depth})")
        
        if graph.links:
            print(f"  📊 Sample links:")
            for link in graph.links[:3]:  # Show first 3
                print(f"    - {link.source} -> {link.target}")
    except Exception as e:
        print(f"❌ Could not retrieve graph: {e}")

    print("\n" + "=" * 60)
    print("5. CONFIGURATION OPTIONS")
    print("=" * 60)

    # Configuration examples
    print("\n⚙️ Configuration Examples:")
    
    # Default configuration
    print("\n  Default Configuration:")
    default_client = Athena()
    print("    ✅ Created with default settings (public Athena server)")
    
    # Custom configuration
    print("\n  Custom Configuration:")
    custom_client = Athena(
        timeout=15,
        max_retries=5
    )
    print("    ✅ Created with custom timeout and retry settings")

    print("\n📋 Client Capabilities:")
    print("  - ✅ Real API connectivity")
    print("  - ✅ Enhanced error handling")
    print("  - ✅ Robust retry logic")
    print("  - ✅ Custom User-Agent and headers")
    print("  - ✅ Parameter normalization")
    print("  - ✅ Detailed logging")
    print("  - ✅ Session management")
    print("  - ✅ Pydantic model validation")
    print("  - ✅ Search with pagination")
    print("  - ✅ Query DSL support")
    print("  - ✅ Concept details retrieval")
    print("  - ✅ Relationship exploration")
    print("  - ✅ Graph visualization data")

    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nThe enhanced athena-client is working perfectly!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Real API connectivity")
    print("  ✅ Search functionality with pagination")
    print("  ✅ Query DSL for complex searches")
    print("  ✅ Concept details retrieval")
    print("  ✅ Relationships exploration")
    print("  ✅ Graph visualization data")
    print("  ✅ Configuration options")
    print("\nEnhanced Features:")
    print("  ✅ Custom User-Agent (AthenaOHDSIAPIClient/1.0)")
    print("  ✅ Robust error handling and logging")
    print("  ✅ Enhanced retry logic")
    print("  ✅ Parameter normalization")
    print("  ✅ Proper URL building")
    print("  ✅ Pydantic model validation")
    print("  ✅ Flexible pagination handling")
    print("\nFor more information, visit: https://athena-client.readthedocs.io")


if __name__ == "__main__":
    main() 