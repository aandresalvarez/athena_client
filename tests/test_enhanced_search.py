"""
Tests for enhanced search functionality with progress tracking.

These tests verify that the enhanced search features work correctly,
including progress tracking for large queries.
"""

import pytest
from unittest.mock import patch, MagicMock

from athena_client import Athena
from athena_client.exceptions import ValidationError


class TestEnhancedSearch:
    """Test enhanced search functionality."""

    def test_search_with_progress_tracking(self):
        """Test search with progress tracking enabled."""
        athena = Athena()
        
        # Mock the search to avoid real API calls
        with patch.object(athena.http, 'get') as mock_get:
            # Mock response data
            mock_response = {
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
                    'totalElements': 1000,
                    'pageSize': 20,
                    'pageNumber': 0
                },
                'totalElements': 1000,
                'last': False,
                'first': True,
                'size': 20,
                'number': 0
            }
            mock_get.return_value = mock_response
            
            # Test search with progress tracking
            results = athena.search('aspirin', size=50, show_progress=True)
            
            # Verify results structure (the actual API call happens in the real implementation)
            assert len(results.all()) == 1
            assert results.total_elements == 1000
            assert results.current_page == 0
            assert results.page_size == 20

    def test_graph_with_progress_tracking(self):
        """Test graph operation with progress tracking."""
        athena = Athena()
        
        # Mock the graph endpoint
        with patch.object(athena.http, 'get') as mock_get:
            # Mock graph response
            mock_response = {
                'terms': [
                    {
                        'id': 12345,
                        'name': 'Test Term',
                        'weight': 1,
                        'depth': 0,
                        'count': 1,
                        'isCurrent': True
                    }
                ],
                'links': [
                    {
                        'source': 12345,
                        'target': 67890,
                        'relationshipId': 'test_rel',
                        'relationshipName': 'Test Relationship'
                    }
                ],
                'connectionsCount': 1
            }
            mock_get.return_value = mock_response
            
            # Test graph with progress tracking
            graph = athena.graph(12345, depth=2, zoom_level=2, show_progress=True)
            
            # Verify graph structure (the actual API call happens in the real implementation)
            assert len(graph.terms) == 1
            assert len(graph.links) == 1
            assert graph.connectionsCount == 1

    def test_large_query_warning(self):
        """Test that large queries show appropriate warnings."""
        athena = Athena()
        
        # Test with a query that would be considered large
        with patch('builtins.print') as mock_print:
            with patch.object(athena.http, 'get') as mock_get:
                mock_get.return_value = {
                    'content': [],
                    'pageable': {'totalElements': 1000},
                    'totalElements': 1000,
                    'last': True,
                    'first': True,
                    'size': 20,
                    'number': 0
                }
                
                # This should trigger a large query warning
                results = athena.search('pain', size=100)
                
                # Verify warning was printed
                mock_print.assert_called()
                # Check that the warning message contains expected text
                calls = [call[0][0] for call in mock_print.call_args_list]
                warning_calls = [call for call in calls if 'matches many concepts' in str(call)]
                assert len(warning_calls) > 0

    def test_page_size_validation(self):
        """Test that page size validation works correctly."""
        athena = Athena()
        
        # Test with page size that exceeds maximum
        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            athena.search('test', size=2000)  # Should exceed max page size

    def test_progress_context_manager(self):
        """Test progress context manager functionality."""
        from athena_client.utils.progress import progress_context, ProgressTracker
        
        # Test progress context with mock
        with patch('athena_client.utils.progress.ProgressTracker') as mock_tracker:
            mock_tracker_instance = MagicMock()
            mock_tracker.return_value = mock_tracker_instance
            
            with progress_context(total=100, description="Test"):
                pass
            
            # Verify progress tracker was created and used
            mock_tracker.assert_called_once()
            mock_tracker_instance.start.assert_called_once()
            mock_tracker_instance.complete.assert_called_once()

    def test_operation_timeout_calculation(self):
        """Test that operation timeouts are calculated correctly."""
        from athena_client.utils import get_operation_timeout
        
        # Test timeout calculation for different operations
        search_timeout = get_operation_timeout("search", query_size=100)
        graph_timeout = get_operation_timeout("graph", query_size=100)
        
        # Verify timeouts are reasonable
        assert search_timeout > 0
        assert graph_timeout > 0
        # Graph operations should typically have longer timeouts
        assert graph_timeout >= search_timeout

    def test_query_size_estimation(self):
        """Test query size estimation functionality."""
        from athena_client.utils import estimate_query_size
        
        # Test size estimation for different query types
        small_query_size = estimate_query_size("aspirin")
        large_query_size = estimate_query_size("pain")
        
        # Verify estimations are reasonable
        assert small_query_size > 0
        assert large_query_size > 0
        # Large queries should have higher estimates
        assert large_query_size >= small_query_size 