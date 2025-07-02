#!/usr/bin/env python3
"""
Concept Exploration Demo

This script demonstrates the ConceptExplorer with:
- Async/await support for improved performance
- BFS-based exploration algorithm
- Batch processing of API calls
- Configurable exploration parameters
- Enhanced error handling

This example works with the lightweight installation:
pip install athena-client

Usage:
    python concept_exploration_demo.py
"""

import asyncio
import logging
import time
from typing import Dict, Any

# Import the athena client
try:
    from athena_client import AthenaClient, create_concept_explorer
    from athena_client.async_client import AthenaAsyncClient
except ImportError:
    print("Please install athena-client: pip install athena-client")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_basic_exploration():
    """Demonstrate basic concept exploration with async client."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Concept Exploration (Async Client)")
    print("="*60)
    
    # Initialize async client
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    query = "migraine"
    print(f"Exploring concepts for: '{query}'")
    
    start_time = time.time()
    
    try:
        # Perform async exploration with limits
        results = await explorer.find_standard_concepts(
            query=query,
            max_exploration_depth=1,  # Reduced depth
            initial_seed_limit=3,     # Reduced seed limit
            include_synonyms=True,
            include_relationships=True,
            max_total_concepts=20,    # Limit total concepts
            max_api_calls=15,         # Limit API calls
            max_time_seconds=20       # Limit time
        )
        
        elapsed_time = time.time() - start_time
        
        # Display results
        print(f"\nExploration completed in {elapsed_time:.2f} seconds")
        print(f"Direct matches: {len(results['direct_matches'])}")
        print(f"Synonym matches: {len(results['synonym_matches'])}")
        print(f"Relationship matches: {len(results['relationship_matches'])}")
        print(f"Cross references: {len(results['cross_references'])}")
        
        # Show exploration statistics
        if 'exploration_stats' in results:
            stats = results['exploration_stats']
            print(f"\n📊 Exploration Statistics:")
            print(f"  Total concepts found: {stats['total_concepts_found']}")
            print(f"  API calls made: {stats['api_calls_made']}")
            print(f"  Time elapsed: {stats['time_elapsed_seconds']:.2f}s")
            print(f"  Limits reached:")
            for limit_type, reached in stats['limits_reached'].items():
                status = "✓" if reached else "✗"
                print(f"    {status} {limit_type}")
        
        # Show some direct matches
        if results['direct_matches']:
            print("\nTop direct matches:")
            for i, concept in enumerate(results['direct_matches'][:3], 1):
                print(f"  {i}. {concept.name} ({concept.vocabulary}) - {concept.standardConcept}")
        
        # Show some synonym matches
        if results['synonym_matches']:
            print("\nTop synonym matches:")
            for i, concept in enumerate(results['synonym_matches'][:3], 1):
                print(f"  {i}. {concept.name} ({concept.vocabulary}) - {concept.standardConcept}")
        
        return results
        
    except Exception as e:
        logger.error(f"Exploration failed: {e}")
        return None


async def demo_mapping_with_confidence():
    """Demonstrate concept mapping with confidence scores."""
    print("\n" + "="*60)
    print("DEMO 2: Concept Mapping with Confidence Scores")
    print("="*60)
    
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    query = "diabetes mellitus"
    print(f"Mapping query: '{query}' to standard concepts")
    
    try:
        # Map to standard concepts with confidence scores and limits
        mappings = await explorer.map_to_standard_concepts(
            query=query,
            target_vocabularies=["SNOMED", "RxNorm"],
            confidence_threshold=0.3
        )
        
        print(f"\nFound {len(mappings)} mappings above confidence threshold:")
        
        for i, mapping in enumerate(mappings[:5], 1):
            concept = mapping['concept']
            confidence = mapping['confidence']
            path = mapping['exploration_path']
            category = mapping['source_category']
            
            print(f"\n  {i}. {concept.name}")
            print(f"     Vocabulary: {concept.vocabulary}")
            print(f"     Confidence: {confidence:.3f}")
            print(f"     Path: {path}")
            print(f"     Category: {category}")
        
        return mappings
        
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        return None


async def demo_performance_comparison():
    """Compare performance between different exploration parameters."""
    print("\n" + "="*60)
    print("DEMO 3: Performance Comparison")
    print("="*60)
    
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    query = "hypertension"
    
    # Test different initial_seed_limit values with strict limits
    seed_limits = [2, 3, 5]
    
    for seed_limit in seed_limits:
        print(f"\nTesting with initial_seed_limit={seed_limit}")
        
        start_time = time.time()
        
        try:
            results = await explorer.find_standard_concepts(
                query=query,
                max_exploration_depth=1,  # Keep depth low for comparison
                initial_seed_limit=seed_limit,
                include_synonyms=True,
                include_relationships=True,
                max_total_concepts=15,    # Strict limit
                max_api_calls=10,         # Strict limit
                max_time_seconds=15       # Strict limit
            )
            
            elapsed_time = time.time() - start_time
            total_concepts = (
                len(results['direct_matches']) +
                len(results['synonym_matches']) +
                len(results['relationship_matches'])
            )
            
            print(f"  Time: {elapsed_time:.2f}s")
            print(f"  Total concepts found: {total_concepts}")
            print(f"  Direct matches: {len(results['direct_matches'])}")
            print(f"  Synonym matches: {len(results['synonym_matches'])}")
            print(f"  Relationship matches: {len(results['relationship_matches'])}")
            
            # Show exploration stats
            if 'exploration_stats' in results:
                stats = results['exploration_stats']
                print(f"  API calls: {stats['api_calls_made']}")
                print(f"  Limits hit: {sum(stats['limits_reached'].values())}")
            
        except Exception as e:
            logger.error(f"Test failed for seed_limit={seed_limit}: {e}")


async def demo_error_handling():
    """Demonstrate error handling in the new implementation."""
    print("\n" + "="*60)
    print("DEMO 4: Error Handling")
    print("="*60)
    
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    # Test with invalid parameters
    print("Testing parameter validation:")
    
    try:
        await explorer.find_standard_concepts(
            query="test",
            max_exploration_depth=-1  # Invalid: negative depth
        )
    except ValueError as e:
        print(f"  ✓ Caught invalid max_exploration_depth: {e}")
    
    try:
        await explorer.find_standard_concepts(
            query="test",
            initial_seed_limit=0  # Invalid: zero seed limit
        )
    except ValueError as e:
        print(f"  ✓ Caught invalid initial_seed_limit: {e}")
    
    try:
        await explorer.find_standard_concepts(
            query="test",
            max_total_concepts=0  # Invalid: zero concepts limit
        )
    except ValueError as e:
        print(f"  ✓ Caught invalid max_total_concepts: {e}")
    
    # Test with non-existent query
    print("\nTesting with non-existent query:")
    try:
        results = await explorer.find_standard_concepts(
            query="this_query_should_not_exist_12345",
            max_exploration_depth=1,
            initial_seed_limit=3,
            max_total_concepts=10,
            max_api_calls=5,
            max_time_seconds=10
        )
        
        print(f"  ✓ Handled empty results gracefully")
        print(f"  Direct matches: {len(results['direct_matches'])}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def demo_alternative_queries():
    """Demonstrate alternative query suggestions."""
    print("\n" + "="*60)
    print("DEMO 5: Alternative Query Suggestions")
    print("="*60)
    
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    queries = ["migraine", "diabetes", "hypertension"]
    
    for query in queries:
        print(f"\nSuggestions for '{query}':")
        try:
            suggestions = await explorer.suggest_alternative_queries(
                query=query,
                max_suggestions=5
            )
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
                
        except Exception as e:
            logger.error(f"Failed to get suggestions for '{query}': {e}")


async def demo_concept_hierarchy():
    """Demonstrate concept hierarchy exploration."""
    print("\n" + "="*60)
    print("DEMO 6: Concept Hierarchy")
    print("="*60)
    
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    # First, find a concept to explore
    try:
        results = await explorer.find_standard_concepts(
            query="migraine",
            max_exploration_depth=1,
            initial_seed_limit=1
        )
        
        if results['direct_matches']:
            concept = results['direct_matches'][0]
            print(f"Exploring hierarchy for: {concept.name} (ID: {concept.id})")
            
            hierarchy = await explorer.get_concept_hierarchy(
                concept_id=concept.id,
                max_depth=2
            )
            
            print(f"  Root concept: {hierarchy['root_concept'].name}")
            print(f"  Parents: {len(hierarchy['parents'])}")
            print(f"  Children: {len(hierarchy['children'])}")
            print(f"  Depth: {hierarchy['depth']}")
            
            if hierarchy['parents']:
                print("\n  Parent concepts:")
                for parent in hierarchy['parents'][:3]:
                    print(f"    - {parent.name} ({parent.vocabularyId})")
            
            if hierarchy['children']:
                print("\n  Child concepts:")
                for child in hierarchy['children'][:3]:
                    print(f"    - {child.name} ({child.vocabularyId})")
        
    except Exception as e:
        logger.error(f"Hierarchy exploration failed: {e}")


async def main():
    """Run all demos."""
    print("Concept Exploration Demo")
    print("This demo showcases the ConceptExplorer with:")
    print("- Async/await support for improved performance")
    print("- BFS-based exploration algorithm")
    print("- Batch processing of API calls")
    print("- Configurable exploration parameters")
    print("- Enhanced error handling")
    
    # Run all demos
    await demo_basic_exploration()
    await demo_mapping_with_confidence()
    await demo_performance_comparison()
    await demo_error_handling()
    await demo_alternative_queries()
    await demo_concept_hierarchy()
    
    print("\n" + "="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 