#!/usr/bin/env python3
"""
Demo showcasing enhanced timeout handling, pagination, and user-friendly error messages.

This demo demonstrates how the athena-client handles:
- Large queries with intelligent timeout adjustment
- Progress tracking for long-running operations
- User-friendly warnings and error messages
- Smart pagination for large result sets
- Enhanced error handling for complex operations
"""
import sys
import os
import time

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.utils import estimate_query_size, format_large_query_warning


def demo_timeout_configuration():
    """Demonstrate enhanced timeout configuration."""
    print("\n⏱️  ENHANCED TIMEOUT CONFIGURATION")
    print("=" * 50)
    
    print("\n1. Default Timeout Settings:")
    print("-" * 35)
    athena = Athena()
    print(f"✅ Default timeout: {athena.http.timeout} seconds")
    print(f"✅ Search timeout: 45 seconds (configurable)")
    print(f"✅ Graph timeout: 60 seconds (configurable)")
    print(f"✅ Relationships timeout: 45 seconds (configurable)")
    
    print("\n2. Query Size Estimation:")
    print("-" * 35)
    test_queries = [
        "pain",
        "diabetes mellitus",
        "aspirin 325mg tablet",
        "acute myocardial infarction",
        "c"
    ]
    
    for query in test_queries:
        estimated_size = estimate_query_size(query)
        print(f"Query: '{query}' -> Estimated {estimated_size:,} results")
    
    print("\n3. Large Query Warnings:")
    print("-" * 35)
    for query in ["pain", "cancer", "diabetes"]:
        warning = format_large_query_warning(query, estimate_query_size(query))
        if warning:
            print(warning)
            print()


def demo_progress_tracking():
    """Demonstrate progress tracking for large operations."""
    print("\n📊 PROGRESS TRACKING")
    print("=" * 50)
    
    print("\n1. Progress Features:")
    print("-" * 25)
    print("✅ Real-time progress bars")
    print("✅ ETA calculations")
    print("✅ Time elapsed tracking")
    print("✅ Configurable update intervals")
    print("✅ Thread-safe progress updates")
    
    print("\n2. Progress Configuration:")
    print("-" * 35)
    from athena_client.settings import get_settings
    settings = get_settings()
    print(f"✅ Show progress: {settings.ATHENA_SHOW_PROGRESS}")
    print(f"✅ Update interval: {settings.ATHENA_PROGRESS_UPDATE_INTERVAL} seconds")
    print(f"✅ Large query threshold: {settings.ATHENA_LARGE_QUERY_THRESHOLD} results")
    
    print("\n3. Progress Examples:")
    print("-" * 25)
    print("• Search operations with >100 results")
    print("• Graph operations with depth >2")
    print("• Relationship queries for complex concepts")
    print("• Large pagination requests")


def demo_enhanced_error_messages():
    """Demonstrate enhanced error messages for large queries."""
    print("\n💬 ENHANCED ERROR MESSAGES")
    print("=" * 50)
    
    print("\n1. Timeout Error Examples:")
    print("-" * 35)
    print("❌ Search timeout: The query 'pain' is taking too long to process.")
    print("   Try:")
    print("   • Using more specific search terms")
    print("   • Adding domain or vocabulary filters")
    print("   • Reducing the page size")
    print("   • Breaking the query into smaller parts")
    
    print("\n2. Graph Timeout Error Examples:")
    print("-" * 40)
    print("❌ Graph timeout: The graph for concept 12345 is too complex.")
    print("   Try:")
    print("   • Reducing the depth (currently 3)")
    print("   • Reducing the zoom level (currently 3)")
    print("   • Using a simpler concept as the starting point")
    print("   • Breaking the request into smaller parts")
    
    print("\n3. Pagination Error Examples:")
    print("-" * 35)
    print("❌ Page size too large: Page size must not be greater than 1000")
    print("   Please reduce the page size to 1000 or less.")


def demo_smart_pagination():
    """Demonstrate smart pagination features."""
    print("\n📄 SMART PAGINATION")
    print("=" * 50)
    
    print("\n1. Pagination Configuration:")
    print("-" * 35)
    from athena_client.settings import get_settings
    settings = get_settings()
    print(f"✅ Default page size: {settings.ATHENA_DEFAULT_PAGE_SIZE}")
    print(f"✅ Maximum page size: {settings.ATHENA_MAX_PAGE_SIZE}")
    print(f"✅ Auto-chunk large queries: {settings.ATHENA_AUTO_CHUNK_LARGE_QUERIES}")
    print(f"✅ Chunk size: {settings.ATHENA_CHUNK_SIZE}")
    
    print("\n2. Pagination Features:")
    print("-" * 25)
    print("✅ Automatic page size validation")
    print("✅ Smart defaults based on query size")
    print("✅ Large query chunking")
    print("✅ Progress tracking for pagination")
    print("✅ Memory-efficient result handling")
    
    print("\n3. Pagination Best Practices:")
    print("-" * 35)
    print("• Use smaller page sizes for large queries")
    print("• Enable progress tracking for pagination")
    print("• Consider chunking very large result sets")
    print("• Monitor memory usage for large datasets")


def demo_large_query_handling():
    """Demonstrate handling of large queries."""
    print("\n🔍 LARGE QUERY HANDLING")
    print("=" * 50)
    
    athena = Athena()
    
    print("\n1. Large Query Detection:")
    print("-" * 30)
    large_queries = [
        "pain",
        "diabetes",
        "cancer",
        "heart disease"
    ]
    
    for query in large_queries:
        estimated_size = estimate_query_size(query)
        print(f"Query: '{query}'")
        print(f"  Estimated size: {estimated_size:,} results")
        print(f"  Timeout: {athena.http.timeout * (2.5 if estimated_size > 10000 else 2.0 if estimated_size > 5000 else 1.5):.0f} seconds")
        print()
    
    print("\n2. Large Query Strategies:")
    print("-" * 30)
    print("✅ Automatic timeout adjustment")
    print("✅ Progress tracking for long operations")
    print("✅ User-friendly warnings")
    print("✅ Smart pagination defaults")
    print("✅ Memory-efficient processing")
    
    print("\n3. Large Query Optimization:")
    print("-" * 35)
    print("• Add specific filters (domain, vocabulary)")
    print("• Use smaller page sizes")
    print("• Enable progress tracking")
    print("• Consider breaking into smaller queries")
    print("• Monitor resource usage")


def demo_complex_graph_operations():
    """Demonstrate complex graph operations with enhanced handling."""
    print("\n🕸️  COMPLEX GRAPH OPERATIONS")
    print("=" * 50)
    
    print("\n1. Graph Complexity Estimation:")
    print("-" * 35)
    graph_configs = [
        (2, 2, "Simple graph"),
        (3, 3, "Complex graph"),
        (4, 4, "Very complex graph"),
        (5, 5, "Extremely complex graph")
    ]
    
    for depth, zoom, description in graph_configs:
        complexity = depth * zoom * 100
        timeout = 60 * (2.5 if complexity > 1000 else 2.0 if complexity > 500 else 1.5)
        print(f"{description}: depth={depth}, zoom={zoom}")
        print(f"  Estimated complexity: {complexity}")
        print(f"  Estimated timeout: {timeout:.0f} seconds")
        print()
    
    print("\n2. Graph Operation Features:")
    print("-" * 35)
    print("✅ Complexity-based timeout adjustment")
    print("✅ Progress tracking for complex graphs")
    print("✅ User warnings for complex operations")
    print("✅ Enhanced error messages")
    print("✅ Automatic retry with backoff")
    
    print("\n3. Graph Optimization Tips:")
    print("-" * 30)
    print("• Start with smaller depth/zoom values")
    print("• Monitor progress for complex graphs")
    print("• Use simpler concepts as starting points")
    print("• Consider breaking into multiple requests")
    print("• Enable progress tracking for visibility")


def demo_best_practices():
    """Demonstrate best practices for large queries."""
    print("\n🎯 BEST PRACTICES")
    print("=" * 50)
    
    print("\n1. Query Optimization:")
    print("-" * 25)
    print("✅ Use specific search terms")
    print("✅ Add domain/vocabulary filters")
    print("✅ Start with smaller page sizes")
    print("✅ Enable progress tracking")
    print("✅ Monitor timeout settings")
    
    print("\n2. Error Handling:")
    print("-" * 25)
    print("✅ Read error messages carefully")
    print("✅ Follow troubleshooting suggestions")
    print("✅ Adjust query parameters as needed")
    print("✅ Use appropriate timeout values")
    print("✅ Implement proper retry logic")
    
    print("\n3. Performance Monitoring:")
    print("-" * 30)
    print("✅ Monitor query execution time")
    print("✅ Track memory usage")
    print("✅ Watch for timeout patterns")
    print("✅ Log large query operations")
    print("✅ Optimize based on usage patterns")
    
    print("\n4. Configuration Recommendations:")
    print("-" * 40)
    print("✅ Set appropriate timeout values")
    print("✅ Enable progress tracking")
    print("✅ Configure reasonable page sizes")
    print("✅ Use smart retry strategies")
    print("✅ Monitor and adjust settings")


def main():
    """Run the comprehensive large query demo."""
    print("🚀 ATHENA CLIENT - ENHANCED LARGE QUERY HANDLING DEMO")
    print("=" * 70)
    print("This demo showcases the enhanced features for handling large queries,")
    print("including intelligent timeouts, progress tracking, and user-friendly")
    print("error messages.")
    print("=" * 70)
    
    demo_timeout_configuration()
    demo_progress_tracking()
    demo_enhanced_error_messages()
    demo_smart_pagination()
    demo_large_query_handling()
    demo_complex_graph_operations()
    demo_best_practices()
    
    print("\n" + "=" * 70)
    print("🎉 LARGE QUERY HANDLING DEMO COMPLETE")
    print("=" * 70)
    print("✅ Enhanced timeout configuration demonstrated")
    print("✅ Progress tracking features shown")
    print("✅ User-friendly error messages displayed")
    print("✅ Smart pagination features explained")
    print("✅ Large query handling strategies outlined")
    print("✅ Best practices for optimization provided")
    print("\nThe athena-client now provides comprehensive support for")
    print("large queries with intelligent timeout handling, progress")
    print("tracking, and user-friendly error messages!")


if __name__ == "__main__":
    main() 