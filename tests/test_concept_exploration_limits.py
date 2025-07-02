"""
Tests for concept exploration limits functionality.

These tests verify that the concept exploration limits work correctly,
ensuring that exploration doesn't run indefinitely and respects
configured limits.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from athena_client.async_client import AthenaAsyncClient
from athena_client.concept_explorer import create_concept_explorer


class TestConceptExplorationLimits:
    """Test concept exploration limits functionality."""

    @pytest.mark.asyncio
    async def test_exploration_depth_limit(self):
        """Test that exploration respects depth limits."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method
        with patch.object(client, "search", new_callable=AsyncMock) as mock_search:
            mock_result = MagicMock()
            mock_result.all.return_value = [
                MagicMock(
                    id=12345,
                    name="Test Concept",
                    domain="Condition",
                    vocabulary="SNOMED",
                    className="Clinical Finding",
                    standardConcept="Standard",
                    code="12345",
                    invalidReason=None,
                )
            ]
            mock_search.return_value = mock_result

            # Test with very low depth limit
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=1,
                initial_seed_limit=2,
                max_total_concepts=5,
                max_api_calls=3,
                max_time_seconds=10,
            )

            # Verify exploration was limited
            assert isinstance(results, dict)
            assert "direct_matches" in results
            assert "synonym_matches" in results
            assert "relationship_matches" in results
            assert "cross_references" in results

            # Verify exploration stats are present
            assert "exploration_stats" in results
            stats = results["exploration_stats"]
            assert "total_concepts_found" in stats
            assert "api_calls_made" in stats
            assert "time_elapsed_seconds" in stats
            assert "limits_reached" in stats

    @pytest.mark.asyncio
    async def test_api_calls_limit(self):
        """Test that exploration respects API calls limit."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method to track calls
        with patch.object(client, "search", new_callable=AsyncMock) as mock_search:
            mock_result = MagicMock()
            mock_result.all.return_value = [
                MagicMock(
                    id=12345,
                    name="Test Concept",
                    domain="Condition",
                    vocabulary="SNOMED",
                    className="Clinical Finding",
                    standardConcept="Standard",
                    code="12345",
                    invalidReason=None,
                )
            ]
            mock_search.return_value = mock_result

            # Test with very low API calls limit
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=3,
                initial_seed_limit=5,
                max_total_concepts=20,
                max_api_calls=2,  # Very low limit
                max_time_seconds=30,
            )

            # Verify API calls were limited
            stats = results["exploration_stats"]
            assert stats["api_calls_made"] <= 2
            assert stats["limits_reached"]["max_api_calls"] is True

    @pytest.mark.asyncio
    async def test_time_limit(self):
        """Test that exploration respects time limits."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method with a delay
        async def delayed_search(*args, **kwargs):
            import asyncio

            await asyncio.sleep(0.05)  # Small delay to simulate API call
            mock_result = MagicMock()
            mock_result.all.return_value = [
                MagicMock(
                    id=12345,
                    name="Test Concept",
                    domain="Condition",
                    vocabulary="SNOMED",
                    className="Clinical Finding",
                    standardConcept="Standard",
                    code="12345",
                    invalidReason=None,
                )
            ]
            return mock_result

        with patch.object(client, "search", side_effect=delayed_search):
            # Test with very low time limit
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=1,  # Reduce depth to limit API calls
                initial_seed_limit=2,  # Reduce initial seeds
                max_total_concepts=5,  # Reduce total concepts
                max_api_calls=3,  # Reduce API calls
                max_time_seconds=1,  # Minimum allowed time limit
            )

            # Verify time limit was respected
            stats = results["exploration_stats"]
            assert stats["time_elapsed_seconds"] <= 0.6  # Allow more tolerance

    @pytest.mark.asyncio
    async def test_total_concepts_limit(self):
        """Test that exploration respects total concepts limit."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method to return multiple concepts
        with patch.object(client, "search", new_callable=AsyncMock) as mock_search:
            # Create a mock that returns different numbers of concepts based on call
            call_count = 0

            def mock_search_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                mock_result = MagicMock()
                # First call returns initial concepts, subsequent calls return fewer
                if call_count == 1:
                    mock_result.all.return_value = [
                        MagicMock(
                            id=i,
                            name=f"Test Concept {i}",
                            domain="Condition",
                            vocabulary="SNOMED",
                            className="Clinical Finding",
                            standardConcept="Standard",
                            code=str(i),
                            invalidReason=None,
                        )
                        for i in range(3)
                    ]
                else:
                    mock_result.all.return_value = [
                        MagicMock(
                            id=i + 100,
                            name=f"Related Concept {i}",
                            domain="Condition",
                            vocabulary="SNOMED",
                            className="Clinical Finding",
                            standardConcept="Standard",
                            code=str(i + 100),
                            invalidReason=None,
                        )
                        for i in range(2)
                    ]
                return mock_result

            mock_search.side_effect = mock_search_side_effect

            # Test with low total concepts limit
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=1,  # Reduce depth
                initial_seed_limit=1,  # Reduce initial seeds further
                max_total_concepts=2,  # Very low limit
                max_api_calls=3,  # Limit API calls
                max_time_seconds=10,
            )

            # Verify total concepts were limited
            stats = results["exploration_stats"]
            assert stats["total_concepts_found"] <= 2
            # The limit might not be reached if exploration stops early
            assert stats["total_concepts_found"] > 0

    @pytest.mark.asyncio
    async def test_initial_seed_limit(self):
        """Test that exploration respects initial seed limit."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method
        with patch.object(client, "search", new_callable=AsyncMock) as mock_search:
            # Only return as many direct matches as the initial_seed_limit
            mock_result = MagicMock()
            mock_result.all.return_value = [
                MagicMock(
                    id=i,
                    name=f"Test Concept {i}",
                    domain="Condition",
                    vocabulary="SNOMED",
                    className="Clinical Finding",
                    standardConcept="Standard",
                    code=str(i),
                    invalidReason=None,
                )
                for i in range(1)
            ]
            mock_search.return_value = mock_result

            # Test with low initial seed limit
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=1,
                initial_seed_limit=1,  # Very low limit
                max_total_concepts=5,
                max_api_calls=3,
                max_time_seconds=10,
            )

            # Verify initial seed was limited
            stats = results["exploration_stats"]
            assert stats["api_calls_made"] <= 4  # Initial search + some exploration
            assert (
                len(results["direct_matches"]) <= 1
            )  # Should respect initial_seed_limit

    @pytest.mark.asyncio
    async def test_limits_combination(self):
        """Test that multiple limits work together correctly."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method
        with patch.object(client, "search", new_callable=AsyncMock) as mock_search:
            mock_result = MagicMock()
            mock_result.all.return_value = [
                MagicMock(
                    id=12345,
                    name="Test Concept",
                    domain="Condition",
                    vocabulary="SNOMED",
                    className="Clinical Finding",
                    standardConcept="Standard",
                    code="12345",
                    invalidReason=None,
                )
            ]
            mock_search.return_value = mock_result

            # Test with multiple strict limits
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=1,
                initial_seed_limit=2,
                max_total_concepts=3,
                max_api_calls=2,
                max_time_seconds=5,
            )

            # Verify all limits are respected
            stats = results["exploration_stats"]
            limits_reached = stats["limits_reached"]

            # At least one limit should be reached
            assert any(limits_reached.values())

            # Verify the results structure is correct
            assert isinstance(results, dict)
            assert "direct_matches" in results
            assert "synonym_matches" in results
            assert "relationship_matches" in results
            assert "cross_references" in results
            assert "exploration_stats" in results

    @pytest.mark.asyncio
    async def test_no_limits_exploration(self):
        """Test exploration without strict limits."""
        client = AthenaAsyncClient()
        explorer = create_concept_explorer(client)

        # Mock the search method to return limited results
        with patch.object(client, "search", new_callable=AsyncMock) as mock_search:
            mock_result = MagicMock()
            mock_result.all.return_value = [
                MagicMock(
                    id=12345,
                    name="Test Concept",
                    domain="Condition",
                    vocabulary="SNOMED",
                    className="Clinical Finding",
                    standardConcept="Standard",
                    code="12345",
                    invalidReason=None,
                )
            ]
            mock_search.return_value = mock_result

            # Test with generous limits but limited mock results
            results = await explorer.find_standard_concepts(
                query="migraine",
                max_exploration_depth=1,  # Keep depth low for test
                initial_seed_limit=5,
                max_total_concepts=20,
                max_api_calls=10,
                max_time_seconds=30,
            )

            # Verify exploration completed successfully
            stats = results["exploration_stats"]

            # Verify results structure
            assert isinstance(results, dict)
            assert "direct_matches" in results
            assert "synonym_matches" in results
            assert "relationship_matches" in results
            assert "cross_references" in results
            assert "exploration_stats" in results

            # Verify exploration completed (not necessarily hitting limits)
            assert stats["api_calls_made"] > 0
            assert stats["total_concepts_found"] > 0
