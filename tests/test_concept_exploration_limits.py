"""
Tests for concept exploration limits functionality.

These tests verify that the concept exploration limits work correctly,
ensuring that exploration doesn't run indefinitely and respects
configured limits.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from athena_client.async_client import AthenaAsyncClient
from athena_client.concept_explorer import create_concept_explorer


class TestConceptExplorationLimits:
    """Test concept exploration limits functionality."""

    @pytest.mark.asyncio
    async def test_exploration_depth_limit(self):
        """Test that exploration respects depth limits."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method
        with patch.object(client, 'search_concepts', new_callable=AsyncMock) as mock_search:
            # Mock response for search
            mock_search.return_value = {
                'content': [
                    {
                        'id': 12345,
                        'name': 'Test Concept',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': '12345',
                        'invalidReason': None
                    }
                ],
                'pageable': {
                    'totalElements': 1,
                    'pageSize': 50,
                    'pageNumber': 0
                },
                'totalElements': 1,
                'last': True,
                'first': True,
                'size': 50,
                'number': 0
            }
            
            # Test with very low depth limit
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=1,
                initial_seed_limit=2,
                max_total_concepts=5,
                max_api_calls=3,
                max_time_seconds=10
            )
            
            # Verify exploration was limited
            assert isinstance(results, dict)
            assert 'direct_matches' in results
            assert 'synonym_matches' in results
            assert 'relationship_matches' in results
            assert 'cross_references' in results
            
            # Verify exploration stats are present
            assert 'exploration_stats' in results
            stats = results['exploration_stats']
            assert 'total_concepts_found' in stats
            assert 'api_calls_made' in stats
            assert 'time_elapsed_seconds' in stats
            assert 'limits_reached' in stats

    @pytest.mark.asyncio
    async def test_api_calls_limit(self):
        """Test that exploration respects API calls limit."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method to track calls
        with patch.object(client, 'search_concepts', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = {
                'content': [
                    {
                        'id': 12345,
                        'name': 'Test Concept',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': '12345',
                        'invalidReason': None
                    }
                ],
                'pageable': {
                    'totalElements': 1,
                    'pageSize': 50,
                    'pageNumber': 0
                },
                'totalElements': 1,
                'last': True,
                'first': True,
                'size': 50,
                'number': 0
            }
            
            # Test with very low API calls limit
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=3,
                initial_seed_limit=5,
                max_total_concepts=20,
                max_api_calls=2,  # Very low limit
                max_time_seconds=30
            )
            
            # Verify API calls were limited
            stats = results['exploration_stats']
            assert stats['api_calls_made'] <= 2
            assert stats['limits_reached']['max_api_calls'] is True

    @pytest.mark.asyncio
    async def test_time_limit(self):
        """Test that exploration respects time limits."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method with a delay
        async def delayed_search(*args, **kwargs):
            import asyncio
            await asyncio.sleep(0.1)  # Small delay to simulate API call
            return {
                'content': [
                    {
                        'id': 12345,
                        'name': 'Test Concept',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': '12345',
                        'invalidReason': None
                    }
                ],
                'pageable': {
                    'totalElements': 1,
                    'pageSize': 50,
                    'pageNumber': 0
                },
                'totalElements': 1,
                'last': True,
                'first': True,
                'size': 50,
                'number': 0
            }
        
        with patch.object(client, 'search_concepts', side_effect=delayed_search):
            # Test with very low time limit
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=3,
                initial_seed_limit=5,
                max_total_concepts=20,
                max_api_calls=10,
                max_time_seconds=0.1  # Very low time limit
            )
            
            # Verify time limit was respected
            stats = results['exploration_stats']
            assert stats['time_elapsed_seconds'] <= 0.2  # Allow some tolerance
            assert stats['limits_reached']['max_time_seconds'] is True

    @pytest.mark.asyncio
    async def test_total_concepts_limit(self):
        """Test that exploration respects total concepts limit."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method to return multiple concepts
        with patch.object(client, 'search_concepts', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = {
                'content': [
                    {
                        'id': i,
                        'name': f'Test Concept {i}',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': str(i),
                        'invalidReason': None
                    } for i in range(10)  # Return 10 concepts
                ],
                'pageable': {
                    'totalElements': 10,
                    'pageSize': 50,
                    'pageNumber': 0
                },
                'totalElements': 10,
                'last': True,
                'first': True,
                'size': 50,
                'number': 0
            }
            
            # Test with low total concepts limit
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=2,
                initial_seed_limit=3,
                max_total_concepts=5,  # Low limit
                max_api_calls=10,
                max_time_seconds=30
            )
            
            # Verify total concepts were limited
            total_concepts = (
                len(results['direct_matches']) +
                len(results['synonym_matches']) +
                len(results['relationship_matches'])
            )
            assert total_concepts <= 5
            stats = results['exploration_stats']
            assert stats['total_concepts_found'] <= 5

    @pytest.mark.asyncio
    async def test_initial_seed_limit(self):
        """Test that exploration respects initial seed limit."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method
        with patch.object(client, 'search_concepts', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = {
                'content': [
                    {
                        'id': i,
                        'name': f'Test Concept {i}',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': str(i),
                        'invalidReason': None
                    } for i in range(20)  # Return 20 concepts
                ],
                'pageable': {
                    'totalElements': 20,
                    'pageSize': 50,
                    'pageNumber': 0
                },
                'totalElements': 20,
                'last': True,
                'first': True,
                'size': 50,
                'number': 0
            }
            
            # Test with low initial seed limit
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=1,
                initial_seed_limit=3,  # Low limit
                max_total_concepts=20,
                max_api_calls=10,
                max_time_seconds=30
            )
            
            # Verify initial seed was limited
            # The explorer should not process more than 3 initial concepts
            stats = results['exploration_stats']
            assert stats['api_calls_made'] <= 4  # Initial search + some exploration

    @pytest.mark.asyncio
    async def test_limits_combination(self):
        """Test that multiple limits work together correctly."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method
        with patch.object(client, 'search_concepts', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = {
                'content': [
                    {
                        'id': 12345,
                        'name': 'Test Concept',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': '12345',
                        'invalidReason': None
                    }
                ],
                'totalElements': 1
            }
            
            # Test with multiple strict limits
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=1,
                initial_seed_limit=2,
                max_total_concepts=3,
                max_api_calls=2,
                max_time_seconds=5
            )
            
            # Verify all limits are respected
            stats = results['exploration_stats']
            limits_reached = stats['limits_reached']
            
            # At least one limit should be reached
            assert any(limits_reached.values())
            
            # Verify the results structure is correct
            assert isinstance(results, dict)
            assert 'direct_matches' in results
            assert 'synonym_matches' in results
            assert 'relationship_matches' in results
            assert 'cross_references' in results
            assert 'exploration_stats' in results

    @pytest.mark.asyncio
    async def test_no_limits_exploration(self):
        """Test exploration without strict limits."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)
        
        # Mock the search_concepts method
        with patch.object(client, 'search_concepts', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = {
                'content': [
                    {
                        'id': 12345,
                        'name': 'Test Concept',
                        'domain': 'Condition',
                        'vocabulary': 'SNOMED',
                        'className': 'Clinical Finding',
                        'standardConcept': 'Standard',
                        'code': '12345',
                        'invalidReason': None
                    }
                ],
                'totalElements': 1
            }
            
            # Test with generous limits
            results = await explorer.find_standard_concepts(
                query='migraine',
                max_exploration_depth=2,
                initial_seed_limit=10,
                max_total_concepts=50,
                max_api_calls=20,
                max_time_seconds=60
            )
            
            # Verify exploration completed without hitting limits
            stats = results['exploration_stats']
            limits_reached = stats['limits_reached']
            
            # No limits should be reached with generous settings
            assert not any(limits_reached.values())
            
            # Verify results structure
            assert isinstance(results, dict)
            assert 'direct_matches' in results
            assert 'synonym_matches' in results
            assert 'relationship_matches' in results
            assert 'cross_references' in results 