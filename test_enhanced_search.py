#!/usr/bin/env python3
"""
Test script to demonstrate enhanced search functionality with progress tracking.
"""

from athena_client import Athena

def test_enhanced_search():
    """Test enhanced search with progress tracking."""
    athena = Athena()
    
    print('Testing enhanced search with large query...')
    print('Searching for "pain" with progress tracking...')
    
    try:
        results = athena.search('pain', size=50, show_progress=True)
        print(f'\n✅ Search completed! Found {len(results)} results')
        print(f'Total elements: {results.total_elements}')
        print(f'Current page: {results.current_page}')
        print(f'Page size: {results.page_size}')
        
        print('\nFirst 3 results:')
        for i, concept in enumerate(results.top(3), 1):
            print(f'  {i}. [{concept.id}] {concept.name} ({concept.vocabulary})')
            
    except Exception as e:
        print(f'❌ Search failed: {e}')

def test_graph_with_progress():
    """Test graph operation with progress tracking."""
    athena = Athena()
    
    print('\nTesting enhanced graph with progress tracking...')
    print('Getting graph for aspirin concept (ID: 1191)...')
    
    try:
        graph = athena.graph(1191, depth=2, zoom_level=2, show_progress=True)
        print(f'\n✅ Graph completed!')
        print(f'Terms: {len(graph.terms)}')
        print(f'Links: {len(graph.links)}')
        
    except Exception as e:
        print(f'❌ Graph failed: {e}')

if __name__ == "__main__":
    test_enhanced_search()
    test_graph_with_progress() 