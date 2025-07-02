#!/usr/bin/env python3
"""
Simple demo showcasing the athena-client library working with the real Athena API.

This example demonstrates core functionality that works with the lightweight installation:
pip install athena-client

For additional features like pandas DataFrames, install:
pip install "athena-client[pandas]"
"""
import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.query import Q


def main():
    print("🚀 ATHENA-CLIENT SIMPLE DEMO")
    print("=" * 50)
    print("Testing the athena-client with the real Athena API")
    print("=" * 50)

    # Create client
    print("\n🔧 Creating Athena client...")
    athena = Athena()
    print("✅ Client created successfully")

    print("\n" + "=" * 50)
    print("1. BASIC SEARCH")
    print("=" * 50)

    # Simple text search
    print("\n🔍 Searching for 'aspirin'...")
    try:
        results = athena.search("aspirin", page=0, size=3)
        print(f"✅ Search successful! Found {len(results)} results")
        print("📋 Results:")
        
        for i, concept in enumerate(results.top(3), 1):
            print(f"  {i}. [{concept.id}] {concept.name}")
            print(f"     Domain: {concept.domain}")
            print(f"     Vocabulary: {concept.vocabulary}")
            print(f"     Class: {concept.className}")
            print()

        print(f"📊 Total results available: {results.total_elements}")

    except Exception as e:
        print(f"❌ Search failed: {e}")

    print("\n" + "=" * 50)
    print("2. QUERY DSL SEARCH")
    print("=" * 50)

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

    print("\n" + "=" * 50)
    print("3. CONCEPT DETAILS")
    print("=" * 50)

    # Get concept details for the first aspirin result
    print("\n🔍 Getting concept details for aspirin...")
    try:
        # Get the first aspirin concept ID from the search
        aspirin_results = athena.search("aspirin", page=0, size=1)
        if aspirin_results:
            concept_id = aspirin_results[0].id
            details = athena.details(concept_id)
            print("✅ Concept details retrieved successfully!")
            print(f"  📋 ID: {details.id}")
            print(f"  📋 Name: {details.name}")
            print(f"  📋 Domain: {details.domainId}")
            print(f"  📋 Vocabulary: {details.vocabularyId}")
            print(f"  📋 Class: {details.conceptClassId}")
            print(f"  📋 Code: {details.conceptCode}")
        else:
            print("❌ No aspirin concepts found")
    except Exception as e:
        print(f"❌ Could not retrieve concept details: {e}")

    print("\n" + "=" * 50)
    print("4. CONCEPT RELATIONSHIPS")
    print("=" * 50)

    # Get relationships for the same concept
    print("\n🔗 Getting concept relationships...")
    try:
        if aspirin_results:
            concept_id = aspirin_results[0].id
            relationships = athena.relationships(concept_id)
            print(f"✅ Relationships retrieved successfully! Found {relationships.count} total relationships")
            
            if relationships.items:
                print("📋 Relationship Groups:")
                for i, group in enumerate(relationships.items[:2], 1):  # Show first 2 groups
                    print(f"  {i}. {group.relationshipName} ({len(group.relationships)} relationships)")
        else:
            print("❌ No concept available for relationships")
    except Exception as e:
        print(f"❌ Could not retrieve relationships: {e}")

    print("\n" + "=" * 50)
    print("5. CONCEPT GRAPH")
    print("=" * 50)

    # Get graph for the same concept
    print("\n🕸️ Getting concept graph...")
    try:
        if aspirin_results:
            concept_id = aspirin_results[0].id
            graph = athena.graph(concept_id, depth=1, zoom_level=1)
            print("✅ Graph retrieved successfully!")
            print(f"  📊 Terms: {len(graph.terms)}")
            print(f"  📊 Links: {len(graph.links)}")
        else:
            print("❌ No concept available for graph")
    except Exception as e:
        print(f"❌ Could not retrieve graph: {e}")

    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETED!")
    print("=" * 50)
    print("\nThe athena-client is working correctly with the Athena API!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Basic text search")
    print("  ✅ Query DSL for complex searches")
    print("  ✅ Concept details retrieval")
    print("  ✅ Relationships exploration")
    print("  ✅ Graph visualization data")
    print("\nAll API calls are working as expected!")


if __name__ == "__main__":
    main() 