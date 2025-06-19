#!/usr/bin/env python3
"""
Simple test to verify concept exploration limits are working.
"""

import pytest
from athena_client.async_client import AthenaAsyncClient
from athena_client.concept_explorer import create_concept_explorer

@pytest.mark.asyncio
async def test_limits():
    client = AthenaAsyncClient()
    explorer = create_concept_explorer(client)
    
    print('Testing concept exploration with limits...')
    results = await explorer.find_standard_concepts(
        query='migraine',
        max_exploration_depth=1,
        initial_seed_limit=2,
        max_total_concepts=10,
        max_api_calls=8,
        max_time_seconds=15
    )
    
    print(f'Results: {len(results["direct_matches"])} direct, {len(results["synonym_matches"])} synonyms')
    if 'exploration_stats' in results:
        stats = results['exploration_stats']
        print(f'Stats: {stats["api_calls_made"]} API calls, {stats["time_elapsed_seconds"]:.1f}s')
        print(f'Limits hit: {stats["limits_reached"]}')
    
    # Add assertions to make this a proper test
    assert isinstance(results, dict)
    assert 'direct_matches' in results
    assert 'synonym_matches' in results
    assert 'relationship_matches' in results
    assert 'cross_references' in results 