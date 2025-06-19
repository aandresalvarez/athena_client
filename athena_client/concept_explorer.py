"""
Advanced concept exploration and mapping utilities.

This module provides tools to help find standard concepts that might not appear
directly in search results, including:
- Concept relationship exploration
- Synonym-based concept discovery
- Vocabulary mapping and cross-references
- Standard concept identification
- Concept hierarchy exploration
"""

import asyncio
import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Set, Union

from .models import Concept, ConceptDetails

logger = logging.getLogger(__name__)


@dataclass
class ExplorationState:
    """
    Internal state management for concept exploration runs.

    This dataclass manages the state of a single exploration run to avoid
    passing multiple state variables through method calls.
    """

    queue: Deque[Any] = field(
        default_factory=deque
    )  # BFS queue: (concept, depth, path)
    visited_ids: Set[int] = field(default_factory=set)  # Set of processed concept IDs
    cache: Dict[int, ConceptDetails] = field(
        default_factory=dict
    )  # In-memory cache for concept details
    results: Dict[str, Any] = field(
        default_factory=lambda: {
            "direct_matches": [],
            "synonym_matches": [],
            "relationship_matches": [],
            "cross_references": [],
            "exploration_paths": [],
        }
    )  # Final results structure
    api_call_count: int = 0  # Count of API calls made
    start_time: float = 0  # Start time of exploration
    max_total_concepts: int = 0  # Maximum total concepts to discover
    max_api_calls: int = 0  # Maximum API calls to make
    max_time_seconds: int = 0  # Maximum time to run exploration

    def __post_init__(self) -> None:
        """Initialize default values for dataclass fields."""
        pass  # All defaults handled by field()


class ConceptExplorer:
    """
    Advanced concept exploration and mapping utilities.

    This class provides methods to help discover standard concepts that might
    not appear directly in search results by exploring relationships, synonyms,
    and cross-references using an optimized BFS algorithm with concurrent processing.
    """

    def __init__(self, client: Any) -> None:
        """Initialize the concept explorer with an Athena client.

        Args:
            client: Athena client instance (can be sync or async)
        """
        self.client = client

    async def find_standard_concepts(
        self,
        query: str,
        max_exploration_depth: int = 2,
        initial_seed_limit: int = 10,  # New parameter per FSD
        include_synonyms: bool = True,
        include_relationships: bool = True,
        vocabulary_priority: Optional[List[str]] = None,
        max_total_concepts: int = 100,  # Limit total concepts found
        max_api_calls: int = 50,  # Limit total API calls
        max_time_seconds: int = 30,  # Limit total execution time
    ) -> Dict[str, Any]:
        """
        Find standard concepts related to a query through exploration.

        This method implements a BFS-based exploration algorithm with concurrent
        batch processing for optimal performance.

        Args:
            query: The search query
            max_exploration_depth: Maximum depth to explore relationships
            initial_seed_limit: Maximum number of top search results to use as seeds
            include_synonyms: Whether to explore synonyms
            include_relationships: Whether to explore relationships
            vocabulary_priority: Preferred vocabularies (e.g., ['SNOMED', 'RxNorm'])
            max_total_concepts: Maximum total concepts to discover
            max_api_calls: Maximum API calls to make
            max_time_seconds: Maximum time to run exploration

        Returns:
            Dictionary containing standard concepts found through exploration
        """
        # Validate parameters
        if max_exploration_depth < 0:
            raise ValueError("max_exploration_depth must be non-negative")
        if initial_seed_limit < 1:
            raise ValueError("initial_seed_limit must be at least 1")
        if max_total_concepts < 1:
            raise ValueError("max_total_concepts must be at least 1")
        if max_api_calls < 1:
            raise ValueError("max_api_calls must be at least 1")
        if max_time_seconds < 1:
            raise ValueError("max_time_seconds must be at least 1")

        # Initialize exploration state with limits
        state = ExplorationState()
        state.api_call_count = 0
        state.start_time = asyncio.get_event_loop().time()
        state.max_total_concepts = max_total_concepts
        state.max_api_calls = max_api_calls
        state.max_time_seconds = max_time_seconds

        # Step 1: Initial search and seeding
        logger.info(f"Performing direct search for: {query}")
        direct_results = await self.client.search(query, size=50)
        state.api_call_count += 1
        all_direct_matches = direct_results.all()
        state.results["direct_matches"] = all_direct_matches

        # Take top initial_seed_limit results as seeds
        seed_concepts = all_direct_matches[:initial_seed_limit]
        logger.info(f"Using {len(seed_concepts)} concepts as exploration seeds")

        # Add seed concepts to queue and mark as visited
        for concept in seed_concepts:
            state.queue.append((concept, 0, [concept.id]))
            state.visited_ids.add(concept.id)

        # Step 2: Main BFS traversal loop
        await self._bfs_exploration_loop(
            state,
            max_exploration_depth,
            include_synonyms,
            include_relationships,
            vocabulary_priority,
        )

        # Step 3: Find cross-references (with limits)
        if state.api_call_count < state.max_api_calls:
            logger.info("Finding cross-references")
            cross_refs = await self._find_cross_references(
                all_direct_matches, vocabulary_priority, state
            )
            state.results["cross_references"] = cross_refs

        # Add exploration statistics
        elapsed_time = asyncio.get_event_loop().time() - state.start_time
        state.results["exploration_stats"] = {
            "total_concepts_found": len(state.visited_ids),
            "api_calls_made": state.api_call_count,
            "time_elapsed_seconds": elapsed_time,
            "limits_reached": {
                "max_concepts": len(state.visited_ids) >= max_total_concepts,
                "max_api_calls": state.api_call_count >= max_api_calls,
                "max_time": elapsed_time >= max_time_seconds,
            },
        }

        return state.results

    async def _bfs_exploration_loop(
        self,
        state: ExplorationState,
        max_exploration_depth: int,
        include_synonyms: bool,
        include_relationships: bool,
        vocabulary_priority: Optional[List[str]] = None,
    ) -> None:
        """
        Main BFS exploration loop with concurrent batch processing.

        Args:
            state: Exploration state object
            max_exploration_depth: Maximum exploration depth
            include_synonyms: Whether to explore synonyms
            include_relationships: Whether to explore relationships
            vocabulary_priority: Preferred vocabularies
        """
        while state.queue:
            # Check limits before processing
            current_time = asyncio.get_event_loop().time()
            elapsed_time = current_time - state.start_time

            # Check if we've hit any limits
            if (
                len(state.visited_ids) >= state.max_total_concepts
                or state.api_call_count >= state.max_api_calls
                or elapsed_time >= state.max_time_seconds
            ):
                logger.info("Exploration stopped due to limits:")
                logger.info(
                    f"  - Concepts found: {len(state.visited_ids)}/"
                    f"{state.max_total_concepts}"
                )
                logger.info(
                    f"  - API calls made: {state.api_call_count}/{state.max_api_calls}"
                )
                logger.info(
                    f"  - Time elapsed: {elapsed_time:.1f}s/{state.max_time_seconds}s"
                )
                break

            # Process all nodes at current depth level
            level_size = len(state.queue)
            ids_to_fetch_details: Set[int] = set()

            logger.info(f"Processing {level_size} concepts at current depth level")

            # Process all nodes at current depth
            for _ in range(level_size):
                # Check limits again in case we've hit them during processing
                if (
                    len(state.visited_ids) >= state.max_total_concepts
                    or state.api_call_count >= state.max_api_calls
                    or asyncio.get_event_loop().time() - state.start_time
                    >= state.max_time_seconds
                ):
                    break

                concept, depth, path = state.queue.popleft()

                # Skip if we've reached max depth
                if depth >= max_exploration_depth:
                    continue

                # Discover neighbors (synonyms and relationships)
                await self._discover_neighbors(
                    concept,
                    depth,
                    path,
                    state,
                    ids_to_fetch_details,
                    include_synonyms,
                    include_relationships,
                )

            # Batch fetch details for all discovered concepts
            if ids_to_fetch_details and state.api_call_count < state.max_api_calls:
                await self._process_batch_results(
                    ids_to_fetch_details, state, depth + 1, vocabulary_priority
                )

    async def _discover_neighbors(
        self,
        concept: Concept,
        depth: int,
        path: List[int],
        state: ExplorationState,
        ids_to_fetch_details: Set[int],
        include_synonyms: bool,
        include_relationships: bool,
    ) -> None:
        """
        Discover neighboring concepts through synonyms and relationships.

        Args:
            concept: Current concept being explored
            depth: Current exploration depth
            path: Path taken to reach this concept
            state: Exploration state
            ids_to_fetch_details: Set to collect IDs for batch fetching
            include_synonyms: Whether to explore synonyms
            include_relationships: Whether to explore relationships
        """
        # Explore synonyms if enabled
        if include_synonyms:
            await self._discover_synonym_neighbors(
                concept, depth, path, state, ids_to_fetch_details
            )

        # Explore relationships if enabled
        if include_relationships:
            await self._discover_relationship_neighbors(
                concept, depth, path, state, ids_to_fetch_details
            )

    async def _discover_synonym_neighbors(
        self,
        concept: Concept,
        depth: int,
        path: List[int],
        state: ExplorationState,
        ids_to_fetch_details: Set[int],
    ) -> None:
        """Discover neighboring concepts through synonyms."""
        if concept.standardConcept == "Standard":
            # For standard concepts, search for synonyms
            try:
                # Check API call limit
                if state.api_call_count >= state.max_api_calls:
                    return

                synonym_results = await self.client.search(concept.name, size=10)
                state.api_call_count += 1

                for synonym_concept in synonym_results.all():
                    if (
                        synonym_concept.id not in state.visited_ids
                        and len(state.visited_ids) < state.max_total_concepts
                    ):
                        ids_to_fetch_details.add(synonym_concept.id)

            except Exception as e:
                logger.warning(
                    f"Could not generate suggestions for query '{concept.name}': {e}"
                )

    async def _discover_relationship_neighbors(
        self,
        concept: Concept,
        depth: int,
        path: List[int],
        state: ExplorationState,
        ids_to_fetch_details: Set[int],
    ) -> None:
        """Discover neighboring concepts through relationships."""
        try:
            # Check API call limit
            if state.api_call_count >= state.max_api_calls:
                return

            relationships = await self.client.relationships(
                concept.id, only_standard=True
            )
            state.api_call_count += 1

            for group in relationships.items:
                for rel in group.relationships:
                    if (
                        rel.targetConceptId not in state.visited_ids
                        and len(state.visited_ids) < state.max_total_concepts
                    ):
                        ids_to_fetch_details.add(rel.targetConceptId)

        except Exception as e:
            logger.warning(f"Could not get relationships for concept {concept.id}: {e}")

    async def _process_batch_results(
        self,
        ids_to_fetch_details: Set[int],
        state: ExplorationState,
        next_depth: int,
        vocabulary_priority: Optional[List[str]] = None,
    ) -> None:
        """Process batch results and add to queue."""
        if not ids_to_fetch_details:
            return

        # Check API call limit
        if state.api_call_count >= state.max_api_calls:
            return

        try:
            # Batch fetch concept details
            concept_details_list = await self._get_details_batch_async(
                ids_to_fetch_details
            )
            state.api_call_count += 1

            # Process each concept detail
            for concept_details in concept_details_list:
                if isinstance(concept_details, BaseException):
                    continue

                # Now we know it's a ConceptDetails object
                concept_details_obj = concept_details  # type: ConceptDetails

                # Convert to Concept object
                concept = Concept(
                    id=concept_details_obj.id,
                    name=concept_details_obj.name,
                    domain=concept_details_obj.domainId,
                    vocabulary=concept_details_obj.vocabularyId,
                    className=concept_details_obj.conceptClassId,
                    standardConcept=concept_details_obj.standardConcept,
                    code=concept_details_obj.conceptCode,
                    invalidReason=concept_details_obj.invalidReason,
                    score=None,  # No score available from concept details
                )

                # Add to appropriate result category
                if concept.standardConcept == "Standard":
                    if concept not in state.results["synonym_matches"]:
                        state.results["synonym_matches"].append(concept)
                else:
                    if concept not in state.results["relationship_matches"]:
                        state.results["relationship_matches"].append(concept)

                # Add to queue for further exploration if within limits
                if (
                    len(state.visited_ids) < state.max_total_concepts
                    and concept.id not in state.visited_ids
                ):
                    # Create a simple path for this concept
                    new_path = [concept.id]
                    state.queue.append((concept, next_depth, new_path))
                    state.visited_ids.add(concept.id)

        except Exception as e:
            logger.warning(f"Error processing batch results: {e}")

    async def _get_details_batch_async(
        self, concept_ids: Set[int]
    ) -> List[Union[ConceptDetails, BaseException]]:
        """
        Fetch concept details for multiple IDs concurrently.

        Args:
            concept_ids: Set of concept IDs to fetch details for

        Returns:
            List of ConceptDetails objects or Exception objects for failed requests
        """
        if not (
            hasattr(self.client, "get_concept_details")
            and asyncio.iscoroutinefunction(self.client.get_concept_details)
        ):
            raise NotImplementedError("Async client not available")

        # Create tasks for concurrent execution
        tasks = [
            self.client.get_concept_details(concept_id) for concept_id in concept_ids
        ]

        # Execute all tasks concurrently with exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    def _extract_standard_concepts(
        self, concepts: List[Concept], vocabulary_priority: Optional[List[str]] = None
    ) -> List[Concept]:
        """Extract standard concepts from a list of concepts."""
        standard_concepts = []

        for concept in concepts:
            if concept.standardConcept == "Standard":
                standard_concepts.append(concept)

        # Sort by vocabulary priority if specified
        if vocabulary_priority:

            def sort_key(concept: Concept) -> int:
                try:
                    return vocabulary_priority.index(concept.vocabulary)
                except ValueError:
                    return len(vocabulary_priority)

            standard_concepts.sort(key=sort_key)

        return standard_concepts

    async def _find_cross_references(
        self,
        concepts: List[Concept],
        vocabulary_priority: Optional[List[str]] = None,
        state: Optional[ExplorationState] = None,
    ) -> List[Dict[str, Any]]:
        """Find cross-references between concepts."""
        cross_refs = []

        for concept in concepts:
            if concept.standardConcept == "Standard":
                # Look for related concepts in other vocabularies
                try:
                    # Check API call limit
                    if state and state.api_call_count >= state.max_api_calls:
                        break

                    relationships = await self.client.relationships(
                        concept.id, only_standard=True
                    )
                    if state:
                        state.api_call_count += 1

                    for group in relationships.items:
                        for rel in group.relationships:
                            cross_ref = {
                                "source_concept": concept,
                                "target_concept_id": rel.targetConceptId,
                                "target_concept_name": rel.targetConceptName,
                                "relationship_type": rel.relationshipName,
                                "vocabulary": rel.targetVocabularyId,
                            }
                            cross_refs.append(cross_ref)

                except Exception as e:
                    logger.warning(
                        f"Could not get relationships for concept {concept.id}: {e}"
                    )

        return cross_refs

    async def map_to_standard_concepts(
        self,
        query: str,
        target_vocabularies: Optional[List[str]] = None,
        confidence_threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Map a query to standard concepts with confidence scores.

        This method is now async to support the new async find_standard_concepts.

        Args:
            query: The search query
            target_vocabularies: Preferred target vocabularies
            confidence_threshold: Minimum confidence score for inclusion

        Returns:
            List of mapping results with confidence scores
        """
        # Get exploration results
        exploration_results = await self.find_standard_concepts(query)

        # Collect all standard concepts
        all_standard_concepts = []
        all_standard_concepts.extend(exploration_results["direct_matches"])
        all_standard_concepts.extend(exploration_results["synonym_matches"])
        all_standard_concepts.extend(exploration_results["relationship_matches"])

        # Filter by target vocabularies if specified
        if target_vocabularies:
            all_standard_concepts = [
                concept
                for concept in all_standard_concepts
                if concept.vocabulary in target_vocabularies
            ]

        # Calculate confidence scores and create mappings
        mappings = []
        for concept in all_standard_concepts:
            confidence = self._calculate_mapping_confidence(
                query, concept, exploration_results
            )

            if confidence >= confidence_threshold:
                mapping = {
                    "concept": concept,
                    "confidence": confidence,
                    "exploration_path": self._get_exploration_path(
                        concept, exploration_results
                    ),
                    "source_category": self._get_source_category(
                        concept, exploration_results
                    ),
                }
                mappings.append(mapping)

        # Sort by confidence score (descending)
        mappings.sort(key=lambda x: x["confidence"], reverse=True)

        return mappings

    def _calculate_mapping_confidence(
        self, query: str, concept: Concept, exploration_results: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a concept mapping."""
        confidence = 0.0

        # Base confidence from search score if available
        if concept.score is not None:
            confidence += concept.score * 0.4

        # Boost for direct matches
        if concept in exploration_results["direct_matches"]:
            confidence += 0.3

        # Boost for synonym matches
        if concept in exploration_results["synonym_matches"]:
            confidence += 0.2

        # Boost for relationship matches
        if concept in exploration_results["relationship_matches"]:
            confidence += 0.1

        # Vocabulary preference boost
        if concept.vocabulary in ["SNOMED", "RxNorm"]:
            confidence += 0.1

        return min(confidence, 1.0)

    def _get_exploration_path(
        self, concept: Concept, exploration_results: Dict[str, Any]
    ) -> str:
        """Get the exploration path that led to this concept."""
        if concept in exploration_results["direct_matches"]:
            return "direct_search"
        elif concept in exploration_results["synonym_matches"]:
            return "synonym_exploration"
        elif concept in exploration_results["relationship_matches"]:
            return "relationship_exploration"
        else:
            return "unknown"

    def _get_source_category(
        self, concept: Concept, exploration_results: Dict[str, Any]
    ) -> str:
        """Get the source category for a concept."""
        if concept in exploration_results["direct_matches"]:
            return "direct_match"
        elif concept in exploration_results["synonym_matches"]:
            return "synonym_match"
        elif concept in exploration_results["relationship_matches"]:
            return "relationship_match"
        else:
            return "unknown"

    async def suggest_alternative_queries(
        self, query: str, max_suggestions: int = 5
    ) -> List[str]:
        """
        Suggest alternative queries based on the original query.

        Args:
            query: The original query
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of alternative query suggestions
        """
        suggestions = []

        # Basic query variations
        base_suggestions = [
            query.lower(),
            query.title(),
            query.upper(),
            f"{query}*",  # Wildcard
            f"*{query}*",  # Contains
        ]

        # Add base suggestions
        suggestions.extend(base_suggestions)

        # Try to find related concepts for more suggestions
        try:
            results = await self.client.search(query, size=10)
            for concept in results.all():
                if concept.name.lower() != query.lower():
                    suggestions.append(concept.name)
        except Exception as e:
            logger.warning(f"Could not generate suggestions for query '{query}': {e}")

        # Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:max_suggestions]

    async def get_concept_hierarchy(
        self, concept_id: int, max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Get the concept hierarchy for a given concept.

        Args:
            concept_id: The concept ID
            max_depth: Maximum depth to explore

        Returns:
            Dictionary containing hierarchy information
        """
        hierarchy: Dict[str, Any] = {
            "root_concept": None,
            "parents": [],
            "children": [],
            "siblings": [],
            "depth": 0,
        }

        try:
            # Get root concept details
            root_details = await self.client.details(concept_id)
            hierarchy["root_concept"] = root_details

            # Initialize typed lists
            parents: List[ConceptDetails] = []
            children: List[ConceptDetails] = []

            # Get relationships
            relationships = await self.client.relationships(
                concept_id, only_standard=True
            )

            for group in relationships.items:
                if group.relationshipName.lower() in ["is a", "isa", "subclass of"]:
                    # Parent relationships
                    for rel in group.relationships:
                        try:
                            parent_details = await self.client.details(
                                rel.targetConceptId
                            )
                            parents.append(parent_details)
                        except Exception as e:
                            logger.warning(
                                f"Could not fetch parent concept "
                                f"{rel.targetConceptId}: {e}"
                            )

                elif group.relationshipName.lower() in ["has subclass", "has subtype"]:
                    # Child relationships
                    for rel in group.relationships:
                        try:
                            child_details = await self.client.details(
                                rel.targetConceptId
                            )
                            children.append(child_details)
                        except Exception as e:
                            logger.warning(
                                f"Could not fetch child concept "
                                f"{rel.targetConceptId}: {e}"
                            )

            # Update hierarchy with typed lists
            hierarchy["parents"] = parents
            hierarchy["children"] = children
            hierarchy["depth"] = len(parents)

        except Exception as e:
            logger.error(f"Could not get hierarchy for concept {concept_id}: {e}")

        return hierarchy


def create_concept_explorer(client: Any) -> ConceptExplorer:
    """
    Create a ConceptExplorer instance with the given client.

    Args:
        client: Athena client instance

    Returns:
        ConceptExplorer instance
    """
    return ConceptExplorer(client)
