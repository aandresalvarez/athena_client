#!/usr/bin/env python3
"""
Graph Demo - Showcase Concept Relationship Graphs

This script demonstrates the graph functionality with concepts that have
actual relationship data in the Athena API.

Usage:
    python examples/graph_demo.py
"""

import sys
import os
import json
from typing import List, Dict, Any

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.models import ConceptRelationsGraph, GraphTerm, GraphLink


def print_separator(title: str):
    """Print a formatted separator with title."""
    print("\n" + "="*60)
    print(f"📊 {title}")
    print("="*60)


def print_concept_info(concept_id: int, name: str, vocabulary: str):
    """Print basic concept information."""
    print(f"\n🔍 Concept: {name}")
    print(f"   ID: {concept_id}")
    print(f"   Vocabulary: {vocabulary}")


def analyze_graph_structure(graph: ConceptRelationsGraph) -> Dict[str, Any]:
    """Analyze the graph structure and return statistics."""
    stats = {
        "total_terms": len(graph.terms),
        "total_links": len(graph.links),
        "connections_count": graph.connectionsCount or 0,
        "depth_distribution": {},
        "weight_distribution": {},
        "current_concept": None,
        "related_concepts": []
    }
    
    # Analyze terms
    for term in graph.terms:
        # Track depth distribution
        depth = term.depth
        stats["depth_distribution"][depth] = stats["depth_distribution"].get(depth, 0) + 1
        
        # Track weight distribution
        weight_range = f"{term.weight//100*100}-{(term.weight//100+1)*100}"
        stats["weight_distribution"][weight_range] = stats["weight_distribution"].get(weight_range, 0) + 1
        
        # Identify current concept (depth 0)
        if term.depth == 0:
            stats["current_concept"] = {
                "id": term.id,
                "name": term.name,
                "weight": term.weight,
                "count": term.count
            }
        else:
            stats["related_concepts"].append({
                "id": term.id,
                "name": term.name,
                "depth": term.depth,
                "weight": term.weight,
                "count": term.count
            })
    
    return stats


def print_graph_statistics(stats: Dict[str, Any]):
    """Print detailed graph statistics."""
    print(f"\n📈 Graph Statistics:")
    print(f"   Total Terms: {stats['total_terms']}")
    print(f"   Total Links: {stats['total_links']}")
    print(f"   Total Connections: {stats['connections_count']:,}")
    
    if stats['current_concept']:
        current = stats['current_concept']
        print(f"\n🎯 Current Concept:")
        print(f"   Name: {current['name']}")
        print(f"   Weight: {current['weight']:,}")
        print(f"   Count: {current['count']:,}")
    
    if stats['related_concepts']:
        print(f"\n🔗 Related Concepts ({len(stats['related_concepts'])}):")
        for i, concept in enumerate(stats['related_concepts'][:5], 1):  # Show first 5
            print(f"   {i}. {concept['name']}")
            print(f"      Depth: {concept['depth']}, Weight: {concept['weight']:,}")
        
        if len(stats['related_concepts']) > 5:
            print(f"   ... and {len(stats['related_concepts']) - 5} more")
    
    if stats['depth_distribution']:
        print(f"\n📊 Depth Distribution:")
        for depth, count in sorted(stats['depth_distribution'].items()):
            depth_name = "Current" if depth == 0 else f"Level {depth}"
            print(f"   {depth_name}: {count} concepts")


def print_graph_links(graph: ConceptRelationsGraph, max_links: int = 10):
    """Print graph links/relationships."""
    if not graph.links:
        print("\n❌ No relationship links found in the graph.")
        return
    
    print(f"\n🔗 Graph Links (showing first {min(max_links, len(graph.links))}):")
    
    # Create a mapping of term IDs to names for easier lookup
    term_map = {term.id: term.name for term in graph.terms}
    
    for i, link in enumerate(graph.links[:max_links], 1):
        source_name = term_map.get(link.source, f"Unknown ({link.source})")
        target_name = term_map.get(link.target, f"Unknown ({link.target})")
        
        print(f"   {i}. {source_name} → {target_name}")
        if link.relationshipName:
            print(f"      Relationship: {link.relationshipName}")


def demo_basic_graph():
    """Demonstrate basic graph functionality with aspirin."""
    print_separator("BASIC GRAPH DEMO - ASPIRIN (RxNorm)")
    
    athena = Athena()
    
    # Use RxNorm aspirin which has graph data
    concept_id = 1112807  # RxNorm aspirin
    concept_name = "aspirin"
    vocabulary = "RxNorm"
    
    print_concept_info(concept_id, concept_name, vocabulary)
    
    try:
        # Get graph with depth 1 and zoom level 1
        print(f"\n🔄 Fetching graph data (depth=1, zoom=1)...")
        graph = athena.graph(concept_id, depth=1, zoom_level=1)
        
        if not graph.terms:
            print("❌ No graph data found for this concept.")
            return
        
        # Analyze and display graph structure
        stats = analyze_graph_structure(graph)
        print_graph_statistics(stats)
        print_graph_links(graph)
        
        return graph
        
    except Exception as e:
        print(f"❌ Error fetching graph: {e}")
        return None


def demo_deep_graph():
    """Demonstrate deeper graph exploration."""
    print_separator("DEEP GRAPH DEMO - ASPIRIN (RxNorm)")
    
    athena = Athena()
    concept_id = 1112807  # RxNorm aspirin
    
    print_concept_info(concept_id, "aspirin", "RxNorm")
    
    # Test different depth and zoom levels
    configurations = [
        (1, 1, "Shallow exploration"),
        (2, 1, "Medium depth"),
        (1, 2, "Higher zoom level"),
        (2, 2, "Deep exploration")
    ]
    
    for depth, zoom, description in configurations:
        print(f"\n🔄 {description} (depth={depth}, zoom={zoom})...")
        
        try:
            graph = athena.graph(concept_id, depth=depth, zoom_level=zoom)
            
            if graph.terms:
                stats = analyze_graph_structure(graph)
                print(f"   ✅ Found {stats['total_terms']} terms, {stats['total_links']} links")
                print(f"   📊 Connections: {stats['connections_count']:,}")
            else:
                print("   ❌ No graph data")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")


def demo_multiple_concepts():
    """Demonstrate graphs for multiple concepts."""
    print_separator("MULTIPLE CONCEPTS GRAPH DEMO")
    
    athena = Athena()
    
    # Test concepts that might have graph data
    test_concepts = [
        (1112807, "aspirin", "RxNorm"),
        (43013024, "acetaminophen", "RxNorm"),
        (40163718, "ibuprofen", "RxNorm"),
        (46275062, "diabetes mellitus", "SNOMED"),
        (316139, "hypertension", "SNOMED")
    ]
    
    for concept_id, name, vocabulary in test_concepts:
        print_concept_info(concept_id, name, vocabulary)
        
        try:
            graph = athena.graph(concept_id, depth=1, zoom_level=1)
            
            if graph.terms:
                stats = analyze_graph_structure(graph)
                print(f"   ✅ Graph data: {stats['total_terms']} terms, {stats['total_links']} links")
                
                # Show a sample of related concepts
                if stats['related_concepts']:
                    sample = stats['related_concepts'][0]
                    print(f"   🔗 Sample relationship: {sample['name']} (depth {sample['depth']})")
            else:
                print("   ❌ No graph data available")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()  # Empty line between concepts


def demo_graph_export():
    """Demonstrate exporting graph data to different formats."""
    print_separator("GRAPH EXPORT DEMO")
    
    athena = Athena()
    concept_id = 1112807  # RxNorm aspirin
    
    print_concept_info(concept_id, "aspirin", "RxNorm")
    
    try:
        graph = athena.graph(concept_id, depth=1, zoom_level=1)
        
        if not graph.terms:
            print("❌ No graph data to export.")
            return
        
        # Export to JSON
        print(f"\n💾 Exporting graph data...")
        
        # Create a structured export
        export_data = {
            "concept_id": concept_id,
            "concept_name": "aspirin",
            "vocabulary": "RxNorm",
            "graph_metadata": {
                "total_terms": len(graph.terms),
                "total_links": len(graph.links),
                "connections_count": graph.connectionsCount
            },
            "terms": [term.model_dump() for term in graph.terms],
            "links": [link.model_dump() for link in graph.links]
        }
        
        # Save to file
        output_file = "output/aspirin_graph.json"
        os.makedirs("output", exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Graph data exported to: {output_file}")
        print(f"📊 Export contains:")
        print(f"   - {len(graph.terms)} terms")
        print(f"   - {len(graph.links)} links")
        print(f"   - {graph.connectionsCount:,} total connections")
        
        # Show a sample of the export
        print(f"\n📄 Sample export structure:")
        print(json.dumps(export_data["graph_metadata"], indent=2))
        
    except Exception as e:
        print(f"❌ Error exporting graph: {e}")


def demo_graph_analysis():
    """Demonstrate advanced graph analysis."""
    print_separator("GRAPH ANALYSIS DEMO")
    
    athena = Athena()
    concept_id = 1112807  # RxNorm aspirin
    
    print_concept_info(concept_id, "aspirin", "RxNorm")
    
    try:
        graph = athena.graph(concept_id, depth=2, zoom_level=1)
        
        if not graph.terms:
            print("❌ No graph data for analysis.")
            return
        
        stats = analyze_graph_structure(graph)
        
        print(f"\n🔬 Advanced Graph Analysis:")
        
        # Find the most connected terms
        term_connections = {}
        for link in graph.links:
            term_connections[link.source] = term_connections.get(link.source, 0) + 1
            term_connections[link.target] = term_connections.get(link.target, 0) + 1
        
        if term_connections:
            most_connected = max(term_connections.items(), key=lambda x: x[1])
            term_name = next((term.name for term in graph.terms if term.id == most_connected[0]), "Unknown")
            print(f"   🎯 Most connected term: {term_name} ({most_connected[1]} connections)")
        
        # Analyze depth distribution
        if stats['depth_distribution']:
            print(f"   📊 Depth analysis:")
            for depth, count in sorted(stats['depth_distribution'].items()):
                percentage = (count / stats['total_terms']) * 100
                depth_name = "Current" if depth == 0 else f"Level {depth}"
                print(f"      {depth_name}: {count} terms ({percentage:.1f}%)")
        
        # Find high-weight terms
        high_weight_terms = [term for term in graph.terms if term.weight > 1000]
        if high_weight_terms:
            print(f"   ⚡ High-weight terms ({len(high_weight_terms)}):")
            for term in high_weight_terms[:3]:  # Show top 3
                print(f"      - {term.name} (weight: {term.weight:,})")
        
    except Exception as e:
        print(f"❌ Error analyzing graph: {e}")


def main():
    """Run all graph demos."""
    print("🚀 ATHENA-CLIENT GRAPH DEMO")
    print("=" * 60)
    print("This demo showcases concept relationship graphs with actual data")
    print("from the Athena API, demonstrating the rich relationship")
    print("information available for medical concepts.")
    print("=" * 60)
    
    # Run all demos
    demo_basic_graph()
    demo_deep_graph()
    demo_multiple_concepts()
    demo_graph_export()
    demo_graph_analysis()
    
    print("\n" + "="*60)
    print("🎉 GRAPH DEMO COMPLETED!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("  ✅ Basic graph retrieval and visualization")
    print("  ✅ Deep graph exploration with different parameters")
    print("  ✅ Multiple concept comparison")
    print("  ✅ Graph data export and analysis")
    print("  ✅ Advanced graph statistics and insights")
    print("\nThe graph functionality provides rich relationship data")
    print("for understanding medical concept connections!")


if __name__ == "__main__":
    main() 