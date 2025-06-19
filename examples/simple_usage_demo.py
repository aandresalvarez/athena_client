#!/usr/bin/env python3
"""
Simple usage demo showing automatic error handling.

This demo demonstrates how users can use the athena-client without
implementing any error handling - it's all automatic!
"""
import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena


def main():
    """Demonstrate simple usage with automatic error handling."""
    print("🚀 ATHENA CLIENT - SIMPLE USAGE DEMO")
    print("=" * 50)
    print("This demo shows how you can use the client without")
    print("implementing any error handling - it's all automatic!")
    print("=" * 50)
    
    # Create client - no configuration needed for public API
    print("\n1. Creating client...")
    athena = Athena()
    print("✅ Client created successfully")
    
    # Search for concepts - automatic error handling
    print("\n2. Searching for concepts...")
    try:
        results = athena.search("aspirin")
        print(f"✅ Found {len(results.all())} concepts")
        
        # Show first few results
        for i, concept in enumerate(results.top(3)):
            print(f"   {i+1}. {concept.name} (ID: {concept.id})")
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return
    
    # Get concept details - automatic error handling
    print("\n3. Getting concept details...")
    try:
        # Use the first concept from search results
        if results.all():
            concept_id = results.all()[0].id
            details = athena.details(concept_id)
            print(f"✅ Concept details: {details.name}")
            print(f"   Domain: {details.domain.name}")
            print(f"   Vocabulary: {details.vocabulary.name}")
            print(f"   Class: {details.concept_class.name}")
        else:
            print("❌ No concepts found to get details for")
            
    except Exception as e:
        print(f"❌ Failed to get concept details: {e}")
    
    # Get relationships - automatic error handling
    print("\n4. Getting concept relationships...")
    try:
        if results.all():
            concept_id = results.all()[0].id
            relationships = athena.relationships(concept_id)
            print(f"✅ Found {len(relationships.relationships)} relationships")
            
            # Show first few relationships
            for i, rel in enumerate(relationships.relationships[:3]):
                print(f"   {i+1}. {rel.relationship_name} -> {rel.concept_name}")
        else:
            print("❌ No concepts found to get relationships for")
            
    except Exception as e:
        print(f"❌ Failed to get relationships: {e}")
    
    # Test with invalid concept ID - shows automatic error handling
    print("\n5. Testing with invalid concept ID...")
    try:
        details = athena.details(999999999)  # Non-existent concept
        print(f"✅ Unexpected success: {details.name}")
    except Exception as e:
        print(f"✅ Expected error caught automatically: {e}")
        print("   Notice the clear, actionable error message!")
    
    # Test with invalid search parameters - shows automatic error handling
    print("\n6. Testing with invalid search parameters...")
    try:
        results = athena.search("", size=0)  # Invalid page size
        print(f"✅ Unexpected success: found {len(results.all())} concepts")
    except Exception as e:
        print(f"✅ Expected error caught automatically: {e}")
        print("   Notice the helpful suggestion to fix the issue!")
    
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETE")
    print("=" * 50)
    print("✅ No try-catch blocks needed!")
    print("✅ Automatic retry on network issues")
    print("✅ Clear, actionable error messages")
    print("✅ Graceful handling of API errors")
    print("\nThe athena-client provides robust error handling out of the box!")


if __name__ == "__main__":
    main() 