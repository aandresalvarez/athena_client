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

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, Counter

from .models import Concept, ConceptDetails, ConceptRelationship, ConceptRelationsGraph
from .exceptions import APIError, AthenaError

logger = logging.getLogger(__name__)


class ConceptExplorer:
    """
    Advanced concept exploration and mapping utilities.
    
    This class provides methods to help discover standard concepts that might
    not appear directly in search results by exploring relationships, synonyms,
    and cross-references.
    """
    
    def __init__(self, client):
        """Initialize the concept explorer with an Athena client.
        
        Args:
            client: Athena client instance
        """
        self.client = client
    
    def find_standard_concepts(
        self, 
        query: str, 
        max_exploration_depth: int = 2,
        include_synonyms: bool = True,
        include_relationships: bool = True,
        vocabulary_priority: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find standard concepts related to a query through exploration.
        
        Args:
            query: The search query
            max_exploration_depth: Maximum depth to explore relationships
            include_synonyms: Whether to explore synonyms
            include_relationships: Whether to explore relationships
            vocabulary_priority: Preferred vocabularies (e.g., ['SNOMED', 'RxNorm'])
            
        Returns:
            Dictionary containing standard concepts found through exploration
        """
        results = {
            'direct_matches': [],
            'synonym_matches': [],
            'relationship_matches': [],
            'cross_references': [],
            'exploration_paths': []
        }
        
        # Step 1: Direct search
        logger.info(f"Performing direct search for: {query}")
        direct_results = self.client.search(query, size=50)
        results['direct_matches'] = direct_results.all()
        
        # Step 2: Find standard concepts in direct results
        standard_concepts = self._extract_standard_concepts(
            direct_results.all(), 
            vocabulary_priority
        )
        
        # Step 3: Explore synonyms if enabled
        if include_synonyms:
            logger.info("Exploring synonyms for non-standard concepts")
            synonym_concepts = self._explore_synonyms(
                direct_results.all(), 
                max_exploration_depth
            )
            results['synonym_matches'] = synonym_concepts
        
        # Step 4: Explore relationships if enabled
        if include_relationships:
            logger.info("Exploring relationships for concepts")
            relationship_concepts = self._explore_relationships(
                direct_results.all(), 
                max_exploration_depth
            )
            results['relationship_matches'] = relationship_concepts
        
        # Step 5: Find cross-references
        logger.info("Finding cross-references")
        cross_refs = self._find_cross_references(
            direct_results.all(), 
            vocabulary_priority
        )
        results['cross_references'] = cross_refs
        
        return results
    
    def _extract_standard_concepts(
        self, 
        concepts: List[Concept], 
        vocabulary_priority: Optional[List[str]] = None
    ) -> List[Concept]:
        """Extract standard concepts from a list of concepts."""
        standard_concepts = []
        
        for concept in concepts:
            if concept.standardConcept == "Standard":
                standard_concepts.append(concept)
        
        # Sort by vocabulary priority if specified
        if vocabulary_priority:
            def sort_key(concept):
                try:
                    return vocabulary_priority.index(concept.vocabulary)
                except ValueError:
                    return len(vocabulary_priority)
            
            standard_concepts.sort(key=sort_key)
        
        return standard_concepts
    
    def _explore_synonyms(
        self, 
        concepts: List[Concept], 
        max_depth: int
    ) -> List[Concept]:
        """Explore synonyms to find standard concepts."""
        found_concepts = []
        explored_ids = set()
        
        for concept in concepts:
            if concept.id in explored_ids:
                continue
                
            try:
                # Get concept details to access synonyms
                details = self.client.details(concept.id)
                
                if details.synonyms:
                    for synonym in details.synonyms:
                        if isinstance(synonym, str):
                            # Search for the synonym
                            synonym_results = self.client.search(synonym, size=10)
                            for synonym_concept in synonym_results.all():
                                if (synonym_concept.standardConcept == "Standard" and 
                                    synonym_concept.id not in explored_ids):
                                    found_concepts.append(synonym_concept)
                                    explored_ids.add(synonym_concept.id)
                
                explored_ids.add(concept.id)
                
            except Exception as e:
                logger.warning(f"Could not explore synonyms for concept {concept.id}: {e}")
        
        return found_concepts
    
    def _explore_relationships(
        self, 
        concepts: List[Concept], 
        max_depth: int
    ) -> List[Concept]:
        """Explore relationships to find standard concepts."""
        found_concepts = []
        explored_ids = set()
        
        for concept in concepts:
            if concept.id in explored_ids:
                continue
                
            try:
                # Get relationships for the concept
                relationships = self.client.relationships(concept.id, only_standard=True)
                
                for group in relationships.items:
                    for rel in group.relationships:
                        if rel.targetConceptId not in explored_ids:
                            # Get the target concept details
                            target_details = self.client.details(rel.targetConceptId)
                            
                            # Create a Concept object from the details
                            target_concept = Concept(
                                id=target_details.id,
                                name=target_details.name,
                                domain=target_details.domainId,
                                vocabulary=target_details.vocabularyId,
                                className=target_details.conceptClassId,
                                standardConcept=target_details.standardConcept,
                                code=target_details.conceptCode,
                                score=None
                            )
                            
                            found_concepts.append(target_concept)
                            explored_ids.add(rel.targetConceptId)
                
                explored_ids.add(concept.id)
                
            except Exception as e:
                logger.warning(f"Could not explore relationships for concept {concept.id}: {e}")
        
        return found_concepts
    
    def _find_cross_references(
        self, 
        concepts: List[Concept], 
        vocabulary_priority: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Find cross-references between vocabularies."""
        cross_refs = []
        
        for concept in concepts:
            try:
                # Get concept details to find cross-references
                details = self.client.details(concept.id)
                
                # Look for links that might indicate cross-references
                if details.links:
                    for link_name, link_data in details.links.items():
                        if 'cross-reference' in link_name.lower() or 'mapping' in link_name.lower():
                            cross_refs.append({
                                'source_concept': concept,
                                'link_type': link_name,
                                'link_data': link_data
                            })
                
            except Exception as e:
                logger.warning(f"Could not find cross-references for concept {concept.id}: {e}")
        
        return cross_refs
    
    def map_to_standard_concepts(
        self, 
        query: str, 
        target_vocabularies: Optional[List[str]] = None,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Map a query to standard concepts in target vocabularies.
        
        Args:
            query: The search query
            target_vocabularies: List of target vocabularies (e.g., ['SNOMED', 'RxNorm'])
            confidence_threshold: Minimum confidence score for mappings
            
        Returns:
            List of mappings with confidence scores
        """
        mappings = []
        
        # Perform comprehensive search
        exploration_results = self.find_standard_concepts(
            query, 
            max_exploration_depth=3,
            include_synonyms=True,
            include_relationships=True,
            vocabulary_priority=target_vocabularies
        )
        
        # Collect all standard concepts
        all_standard_concepts = []
        all_standard_concepts.extend(exploration_results['direct_matches'])
        all_standard_concepts.extend(exploration_results['synonym_matches'])
        all_standard_concepts.extend(exploration_results['relationship_matches'])
        
        # Filter by target vocabularies if specified
        if target_vocabularies:
            filtered_concepts = []
            for concept in all_standard_concepts:
                if concept.vocabulary in target_vocabularies:
                    filtered_concepts.append(concept)
            all_standard_concepts = filtered_concepts
        
        # Calculate confidence scores and create mappings
        for concept in all_standard_concepts:
            confidence = self._calculate_mapping_confidence(
                query, concept, exploration_results
            )
            
            if confidence >= confidence_threshold:
                mappings.append({
                    'query': query,
                    'concept': concept,
                    'confidence': confidence,
                    'exploration_path': self._get_exploration_path(concept, exploration_results)
                })
        
        # Sort by confidence
        mappings.sort(key=lambda x: x['confidence'], reverse=True)
        
        return mappings
    
    def _calculate_mapping_confidence(
        self, 
        query: str, 
        concept: Concept, 
        exploration_results: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a concept mapping."""
        confidence = 0.0
        
        # Base confidence from search score
        if concept.score:
            confidence += concept.score * 0.4
        
        # Boost for direct matches
        if concept in exploration_results['direct_matches']:
            confidence += 0.3
        
        # Boost for synonym matches
        if concept in exploration_results['synonym_matches']:
            confidence += 0.2
        
        # Boost for relationship matches
        if concept in exploration_results['relationship_matches']:
            confidence += 0.1
        
        # Boost for standard concepts
        if concept.standardConcept == "Standard":
            confidence += 0.2
        
        # Text similarity boost
        query_lower = query.lower()
        concept_name_lower = concept.name.lower()
        
        if query_lower in concept_name_lower or concept_name_lower in query_lower:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _get_exploration_path(
        self, 
        concept: Concept, 
        exploration_results: Dict[str, Any]
    ) -> str:
        """Get the exploration path that led to this concept."""
        if concept in exploration_results['direct_matches']:
            return "direct_match"
        elif concept in exploration_results['synonym_matches']:
            return "synonym_exploration"
        elif concept in exploration_results['relationship_matches']:
            return "relationship_exploration"
        else:
            return "unknown"
    
    def suggest_alternative_queries(
        self, 
        query: str, 
        max_suggestions: int = 5
    ) -> List[str]:
        """
        Suggest alternative queries when standard concepts are not found.
        
        Args:
            query: The original query
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of alternative query suggestions
        """
        suggestions = []
        
        # Common medical term variations
        variations = [
            query.lower(),
            query.title(),
            query.upper(),
        ]
        
        # Add common medical prefixes/suffixes
        medical_terms = [
            f"{query} syndrome",
            f"{query} disease", 
            f"{query} disorder",
            f"{query} condition",
            f"{query} medication",
            f"{query} drug",
        ]
        
        suggestions.extend(variations)
        suggestions.extend(medical_terms)
        
        # Remove duplicates and limit results
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:max_suggestions]
    
    def get_concept_hierarchy(
        self, 
        concept_id: int, 
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Get the concept hierarchy for a given concept.
        
        Args:
            concept_id: The concept ID
            max_depth: Maximum depth to explore
            
        Returns:
            Dictionary containing the concept hierarchy
        """
        hierarchy = {
            'root_concept': None,
            'parents': [],
            'children': [],
            'siblings': [],
            'depth': 0
        }
        
        try:
            # Get the root concept
            root_details = self.client.details(concept_id)
            hierarchy['root_concept'] = root_details
            
            # Get relationships to explore hierarchy
            relationships = self.client.relationships(concept_id)
            
            for group in relationships.items:
                group_name = group.relationshipName.lower()
                
                if 'parent' in group_name or 'is a' in group_name:
                    hierarchy['parents'].extend(group.relationships)
                elif 'child' in group_name or 'has subtype' in group_name:
                    hierarchy['children'].extend(group.relationships)
                elif 'sibling' in group_name or 'broader' in group_name:
                    hierarchy['siblings'].extend(group.relationships)
            
        except Exception as e:
            logger.error(f"Could not get hierarchy for concept {concept_id}: {e}")
        
        return hierarchy


def create_concept_explorer(client) -> ConceptExplorer:
    """Create a ConceptExplorer instance with the given client.
    
    Args:
        client: Athena client instance
        
    Returns:
        ConceptExplorer instance
    """
    return ConceptExplorer(client) 