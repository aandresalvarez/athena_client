#!/usr/bin/env python3
"""
Concept Exploration Demo - Finding Standard Concepts

This demo showcases how to use the concept exploration functionality to find
standard concepts that might not appear directly in search results.

Key features demonstrated:
- Synonym-based concept discovery
- Relationship exploration
- Cross-vocabulary mapping
- Confidence scoring
- Alternative query suggestions
- Concept hierarchy exploration
"""

import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena, ConceptExplorer, create_concept_explorer


def demo_basic_concept_exploration():
    """Demonstrate basic concept exploration functionality."""
    print("\n🔍 BASIC CONCEPT EXPLORATION")
    print("=" * 50)
    
    # Create client and explorer
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    # Example: Search for a term that might not have direct standard concept matches
    query = "headache"
    print(f"\nSearching for: '{query}'")
    
    try:
        # Perform comprehensive exploration
        results = explorer.find_standard_concepts(
            query=query,
            max_exploration_depth=2,
            include_synonyms=True,
            include_relationships=True,
            vocabulary_priority=['SNOMED', 'RxNorm', 'ICD10']
        )
        
        print(f"✅ Exploration completed!")
        print(f"📊 Results summary:")
        print(f"  - Direct matches: {len(results['direct_matches'])}")
        print(f"  - Synonym matches: {len(results['synonym_matches'])}")
        print(f"  - Relationship matches: {len(results['relationship_matches'])}")
        print(f"  - Cross-references: {len(results['cross_references'])}")
        
        # Show standard concepts found
        all_standard = []
        all_standard.extend(results['direct_matches'])
        all_standard.extend(results['synonym_matches'])
        all_standard.extend(results['relationship_matches'])
        
        standard_concepts = [c for c in all_standard if c.standardConcept == "Standard"]
        
        print(f"\n🎯 Standard concepts found: {len(standard_concepts)}")
        for i, concept in enumerate(standard_concepts[:5], 1):
            print(f"  {i}. [{concept.id}] {concept.name}")
            print(f"     Vocabulary: {concept.vocabulary}")
            print(f"     Domain: {concept.domain}")
            print(f"     Code: {concept.code}")
            print()
            
    except Exception as e:
        print(f"❌ Exploration failed: {e}")


def demo_mapping_to_standard_concepts():
    """Demonstrate mapping queries to standard concepts with confidence scores."""
    print("\n🗺️ MAPPING TO STANDARD CONCEPTS")
    print("=" * 50)
    
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    # Example queries that might not have direct standard concept matches
    test_queries = [
        "migraine",
        "hypertension", 
        "diabetes",
        "asthma"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Mapping: '{query}'")
        try:
            mappings = explorer.map_to_standard_concepts(
                query=query,
                target_vocabularies=['SNOMED', 'RxNorm', 'ICD10'],
                confidence_threshold=0.3
            )
            
            print(f"✅ Found {len(mappings)} mappings")
            
            for i, mapping in enumerate(mappings[:3], 1):
                concept = mapping['concept']
                confidence = mapping['confidence']
                path = mapping['exploration_path']
                
                print(f"  {i}. [{concept.id}] {concept.name}")
                print(f"     Vocabulary: {concept.vocabulary}")
                print(f"     Confidence: {confidence:.2f}")
                print(f"     Path: {path}")
                print()
                
        except Exception as e:
            print(f"❌ Mapping failed: {e}")


def demo_alternative_query_suggestions():
    """Demonstrate alternative query suggestions."""
    print("\n💡 ALTERNATIVE QUERY SUGGESTIONS")
    print("=" * 50)
    
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    # Example queries that might need alternatives
    test_queries = [
        "heart attack",
        "high blood pressure",
        "sugar disease"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Original query: '{query}'")
        
        try:
            suggestions = explorer.suggest_alternative_queries(query, max_suggestions=8)
            
            print(f"💡 Alternative suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
                
            # Test one of the suggestions
            if suggestions:
                test_suggestion = suggestions[0]
                print(f"\n🧪 Testing suggestion: '{test_suggestion}'")
                
                test_results = athena.search(test_suggestion, size=3)
                standard_found = [c for c in test_results.all() if c.standardConcept == "Standard"]
                
                print(f"   Found {len(standard_found)} standard concepts")
                for concept in standard_found[:2]:
                    print(f"   - [{concept.id}] {concept.name} ({concept.vocabulary})")
                    
        except Exception as e:
            print(f"❌ Suggestion failed: {e}")


def demo_concept_hierarchy_exploration():
    """Demonstrate concept hierarchy exploration."""
    print("\n🌳 CONCEPT HIERARCHY EXPLORATION")
    print("=" * 50)
    
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    # First, find a concept to explore
    print("\n🔍 Finding a concept to explore...")
    try:
        search_results = athena.search("diabetes", size=5)
        if search_results:
            # Use the first result
            concept = search_results[0]
            print(f"✅ Exploring hierarchy for: [{concept.id}] {concept.name}")
            
            hierarchy = explorer.get_concept_hierarchy(concept.id, max_depth=2)
            
            print(f"\n📊 Hierarchy summary:")
            print(f"  - Root concept: {hierarchy['root_concept'].name if hierarchy['root_concept'] else 'None'}")
            print(f"  - Parents: {len(hierarchy['parents'])}")
            print(f"  - Children: {len(hierarchy['children'])}")
            print(f"  - Siblings: {len(hierarchy['siblings'])}")
            
            # Show some relationships
            if hierarchy['parents']:
                print(f"\n👆 Parent relationships:")
                for i, parent in enumerate(hierarchy['parents'][:3], 1):
                    print(f"  {i}. {parent.relationshipName}: {parent.targetConceptName}")
                    
            if hierarchy['children']:
                print(f"\n👇 Child relationships:")
                for i, child in enumerate(hierarchy['children'][:3], 1):
                    print(f"  {i}. {child.relationshipName}: {child.targetConceptName}")
                    
        else:
            print("❌ No concepts found to explore")
            
    except Exception as e:
        print(f"❌ Hierarchy exploration failed: {e}")


def demo_comprehensive_workflow():
    """Demonstrate a comprehensive workflow for finding standard concepts."""
    print("\n🔄 COMPREHENSIVE WORKFLOW")
    print("=" * 50)
    
    athena = Athena()
    explorer = create_concept_explorer(athena)
    
    # Example: Finding standard concepts for a complex medical term
    query = "myocardial infarction"
    print(f"\n🎯 Target: Find standard concepts for '{query}'")
    
    try:
        # Step 1: Try direct search first
        print("\n1️⃣ Step 1: Direct search")
        direct_results = athena.search(query, size=10)
        direct_standard = [c for c in direct_results.all() if c.standardConcept == "Standard"]
        print(f"   Found {len(direct_standard)} standard concepts directly")
        
        if not direct_standard:
            print("   ⚠️ No standard concepts found directly, exploring...")
            
            # Step 2: Use concept exploration
            print("\n2️⃣ Step 2: Concept exploration")
            exploration_results = explorer.find_standard_concepts(
                query=query,
                max_exploration_depth=3,
                include_synonyms=True,
                include_relationships=True
            )
            
            # Step 3: Get mappings with confidence scores
            print("\n3️⃣ Step 3: Mapping with confidence scores")
            mappings = explorer.map_to_standard_concepts(
                query=query,
                confidence_threshold=0.4
            )
            
            print(f"   Found {len(mappings)} high-confidence mappings")
            
            # Step 4: Show best matches
            print("\n4️⃣ Step 4: Best matches")
            for i, mapping in enumerate(mappings[:5], 1):
                concept = mapping['concept']
                confidence = mapping['confidence']
                path = mapping['exploration_path']
                
                print(f"   {i}. [{concept.id}] {concept.name}")
                print(f"      Vocabulary: {concept.vocabulary}")
                print(f"      Domain: {concept.domain}")
                print(f"      Confidence: {confidence:.2f}")
                print(f"      Discovery path: {path}")
                print()
                
            # Step 5: Explore hierarchy for the best match
            if mappings:
                best_concept = mappings[0]['concept']
                print(f"\n5️⃣ Step 5: Exploring hierarchy for best match")
                print(f"   Exploring: [{best_concept.id}] {best_concept.name}")
                
                hierarchy = explorer.get_concept_hierarchy(best_concept.id, max_depth=1)
                
                if hierarchy['parents']:
                    print(f"   👆 Parent concepts:")
                    for parent in hierarchy['parents'][:2]:
                        print(f"      - {parent.targetConceptName} ({parent.relationshipName})")
                        
        else:
            print("   ✅ Found standard concepts directly!")
            for concept in direct_standard[:3]:
                print(f"      - [{concept.id}] {concept.name} ({concept.vocabulary})")
                
    except Exception as e:
        print(f"❌ Workflow failed: {e}")


def main():
    """Run the concept exploration demo."""
    print("🚀 ATHENA CLIENT - CONCEPT EXPLORATION DEMO")
    print("=" * 60)
    print("This demo showcases advanced concept exploration features")
    print("to help find standard concepts that might not appear")
    print("directly in search results.")
    print("=" * 60)
    
    demo_basic_concept_exploration()
    demo_mapping_to_standard_concepts()
    demo_alternative_query_suggestions()
    demo_concept_hierarchy_exploration()
    demo_comprehensive_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 CONCEPT EXPLORATION DEMO COMPLETED!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("  ✅ Synonym-based concept discovery")
    print("  ✅ Relationship exploration")
    print("  ✅ Cross-vocabulary mapping")
    print("  ✅ Confidence scoring")
    print("  ✅ Alternative query suggestions")
    print("  ✅ Concept hierarchy exploration")
    print("  ✅ Comprehensive workflow for finding standard concepts")
    print("\nThese features help bridge the gap between user queries")
    print("and standard medical concepts in the vocabulary.")


if __name__ == "__main__":
    main() 