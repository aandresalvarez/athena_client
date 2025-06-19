"""
Tests for ConceptExplorer functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from athena_client.concept_explorer import ConceptExplorer, create_concept_explorer
from athena_client.models import Concept, ConceptDetails, ConceptRelationship, ConceptType


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return Mock()


@pytest.fixture
def mock_search_result():
    """Create a mock search result."""
    result = Mock()
    result.all.return_value = [
        Concept(
            id=1,
            name="Test Concept 1",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept=ConceptType.STANDARD,
            code="12345",
            score=0.9
        ),
        Concept(
            id=2,
            name="Test Concept 2",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept=ConceptType.NON_STANDARD,
            code="12346",
            score=0.8
        )
    ]
    return result


@pytest.fixture
def mock_concept_details():
    """Create mock concept details."""
    return ConceptDetails(
        id=2,
        name="Test Concept 2",
        domainId="Condition",
        vocabularyId="SNOMED",
        conceptClassId="Clinical Finding",
        standardConcept=ConceptType.NON_STANDARD,
        conceptCode="12346",
        validStart="2020-01-01",
        validEnd="2099-12-31",
        synonyms=["Alternative Name", "Another Term"],
        validTerm="Test Concept 2",
        vocabularyName="SNOMED CT",
        vocabularyVersion="2023-01-31",
        vocabularyReference="http://snomed.info/sct",
        links={}
    )


@pytest.fixture
def mock_relationships():
    """Create mock relationships."""
    from athena_client.models import RelationshipGroup, RelationshipItem
    
    return ConceptRelationship(
        count=2,
        items=[
            RelationshipGroup(
                relationshipName="Is a",
                relationships=[
                    RelationshipItem(
                        targetConceptId=3,
                        targetConceptName="Parent Concept",
                        targetVocabularyId="SNOMED",
                        relationshipId="116680003",
                        relationshipName="Is a"
                    )
                ]
            )
        ]
    )


class TestConceptExplorer:
    """Test cases for ConceptExplorer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.explorer = ConceptExplorer(self.mock_client)

    def test_init(self):
        """Test ConceptExplorer initialization."""
        assert self.explorer.client == self.mock_client

    def test_extract_standard_concepts(self, mock_search_result):
        """Test extracting standard concepts from search results."""
        concepts = mock_search_result.all()
        standard_concepts = self.explorer._extract_standard_concepts(concepts)
        
        assert len(standard_concepts) == 1
        assert standard_concepts[0].id == 1
        assert standard_concepts[0].standardConcept == ConceptType.STANDARD

    def test_extract_standard_concepts_with_priority(self, mock_search_result):
        """Test extracting standard concepts with vocabulary priority."""
        concepts = mock_search_result.all()
        vocabulary_priority = ["RxNorm", "SNOMED"]
        
        standard_concepts = self.explorer._extract_standard_concepts(
            concepts, vocabulary_priority
        )
        
        assert len(standard_concepts) == 1
        # Should be sorted by vocabulary priority
        assert standard_concepts[0].vocabulary == "SNOMED"

    @patch.object(ConceptExplorer, '_explore_synonyms')
    @patch.object(ConceptExplorer, '_explore_relationships')
    @patch.object(ConceptExplorer, '_find_cross_references')
    def test_find_standard_concepts(
        self, 
        mock_find_cross_refs, 
        mock_explore_relationships, 
        mock_explore_synonyms,
        mock_search_result
    ):
        """Test find_standard_concepts method."""
        # Setup mocks
        self.mock_client.search.return_value = mock_search_result
        mock_explore_synonyms.return_value = []
        mock_explore_relationships.return_value = []
        mock_find_cross_refs.return_value = []
        
        # Call method
        results = self.explorer.find_standard_concepts(
            query="test",
            max_exploration_depth=2,
            include_synonyms=True,
            include_relationships=True
        )
        
        # Verify results structure
        assert 'direct_matches' in results
        assert 'synonym_matches' in results
        assert 'relationship_matches' in results
        assert 'cross_references' in results
        assert 'exploration_paths' in results
        
        # Verify client was called
        self.mock_client.search.assert_called_once_with("test", size=50)

    def test_explore_synonyms(self, mock_concept_details, mock_search_result):
        """Test synonym exploration."""
        # Setup mocks
        self.mock_client.details.return_value = mock_concept_details
        self.mock_client.search.return_value = mock_search_result
        
        concepts = [Concept(
            id=2,
            name="Test Concept 2",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept=ConceptType.NON_STANDARD,
            code="12346",
            score=0.8
        )]
        
        # Call method
        found_concepts = self.explorer._explore_synonyms(concepts, max_depth=1)
        
        # Verify client calls
        self.mock_client.details.assert_called_once_with(2)
        # Should be called for each synonym
        assert self.mock_client.search.call_count >= 1

    def test_explore_relationships(self, mock_relationships, mock_concept_details):
        """Test relationship exploration."""
        # Setup mocks
        self.mock_client.relationships.return_value = mock_relationships
        self.mock_client.details.return_value = mock_concept_details
        
        concepts = [Concept(
            id=2,
            name="Test Concept 2",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept=ConceptType.NON_STANDARD,
            code="12346",
            score=0.8
        )]
        
        # Call method
        found_concepts = self.explorer._explore_relationships(concepts, max_depth=1)
        
        # Verify client calls
        self.mock_client.relationships.assert_called_once_with(2, only_standard=True)
        self.mock_client.details.assert_called_once_with(3)

    def test_find_cross_references(self, mock_concept_details):
        """Test cross-reference finding."""
        # Setup mock with links
        mock_concept_details.links = {
            "cross-reference": {"href": "http://example.com"},
            "mapping": {"href": "http://example.com/map"}
        }
        
        self.mock_client.details.return_value = mock_concept_details
        
        concepts = [Concept(
            id=2,
            name="Test Concept 2",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept=ConceptType.NON_STANDARD,
            code="12346",
            score=0.8
        )]
        
        # Call method
        cross_refs = self.explorer._find_cross_references(concepts)
        
        # Verify results
        assert len(cross_refs) == 2  # Both cross-reference and mapping
        assert cross_refs[0]['source_concept'].id == 2
        assert 'cross-reference' in cross_refs[0]['link_type']

    def test_calculate_mapping_confidence(self, mock_search_result):
        """Test confidence calculation."""
        concepts = mock_search_result.all()
        concept = concepts[0]  # Standard concept with score 0.9
        
        exploration_results = {
            'direct_matches': concepts,
            'synonym_matches': [],
            'relationship_matches': []
        }
        
        confidence = self.explorer._calculate_mapping_confidence(
            "test", concept, exploration_results
        )
        
        # Should have high confidence for standard concept in direct matches
        assert confidence > 0.5
        assert confidence <= 1.0

    def test_get_exploration_path(self, mock_search_result):
        """Test exploration path determination."""
        concepts = mock_search_result.all()
        concept = concepts[0]
        
        exploration_results = {
            'direct_matches': concepts,
            'synonym_matches': [],
            'relationship_matches': []
        }
        
        path = self.explorer._get_exploration_path(concept, exploration_results)
        assert path == "direct_match"

    def test_suggest_alternative_queries(self):
        """Test alternative query suggestions."""
        query = "diabetes"
        suggestions = self.explorer.suggest_alternative_queries(query, max_suggestions=5)
        
        assert len(suggestions) <= 5
        assert query.lower() in suggestions
        assert "diabetes disease" in suggestions
        # Check that we get some medical term variations
        medical_terms = [s for s in suggestions if "syndrome" in s or "disease" in s or "disorder" in s]
        assert len(medical_terms) > 0

    def test_get_concept_hierarchy(self, mock_relationships, mock_concept_details):
        """Test concept hierarchy retrieval."""
        # Setup mocks
        self.mock_client.details.return_value = mock_concept_details
        self.mock_client.relationships.return_value = mock_relationships
        
        hierarchy = self.explorer.get_concept_hierarchy(2, max_depth=2)
        
        # Verify structure
        assert 'root_concept' in hierarchy
        assert 'parents' in hierarchy
        assert 'children' in hierarchy
        assert 'siblings' in hierarchy
        assert 'depth' in hierarchy
        
        # Verify client calls
        self.mock_client.details.assert_called_once_with(2)
        self.mock_client.relationships.assert_called_once_with(2)

    @patch.object(ConceptExplorer, 'find_standard_concepts')
    def test_map_to_standard_concepts(self, mock_find_standard, mock_search_result):
        """Test mapping to standard concepts."""
        # Setup mock
        mock_find_standard.return_value = {
            'direct_matches': mock_search_result.all(),
            'synonym_matches': [],
            'relationship_matches': []
        }
        
        mappings = self.explorer.map_to_standard_concepts(
            query="test",
            target_vocabularies=["SNOMED"],
            confidence_threshold=0.5
        )
        
        # Verify results
        assert len(mappings) > 0
        assert 'query' in mappings[0]
        assert 'concept' in mappings[0]
        assert 'confidence' in mappings[0]
        assert 'exploration_path' in mappings[0]
        
        # Verify sorting by confidence
        confidences = [m['confidence'] for m in mappings]
        assert confidences == sorted(confidences, reverse=True)


class TestCreateConceptExplorer:
    """Test cases for create_concept_explorer function."""

    def test_create_concept_explorer(self):
        """Test create_concept_explorer function."""
        mock_client = Mock()
        explorer = create_concept_explorer(mock_client)
        
        assert isinstance(explorer, ConceptExplorer)
        assert explorer.client == mock_client


class TestConceptExplorerIntegration:
    """Integration tests for ConceptExplorer."""

    def test_error_handling_in_exploration(self):
        """Test error handling during exploration."""
        mock_client = Mock()
        mock_client.search.side_effect = Exception("API Error")
        
        explorer = ConceptExplorer(mock_client)
        
        # Should handle errors gracefully
        with pytest.raises(Exception):
            explorer.find_standard_concepts("test")

    def test_empty_results_handling(self):
        """Test handling of empty search results."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.all.return_value = []
        mock_client.search.return_value = mock_result
        
        explorer = ConceptExplorer(mock_client)
        
        results = explorer.find_standard_concepts("nonexistent")
        
        assert len(results['direct_matches']) == 0
        assert len(results['synonym_matches']) == 0
        assert len(results['relationship_matches']) == 0

    def test_vocabulary_filtering(self, mock_search_result):
        """Test vocabulary filtering in mappings."""
        mock_client = Mock()
        mock_client.search.return_value = mock_search_result
        
        explorer = ConceptExplorer(mock_client)
        
        # Mock the find_standard_concepts method
        with patch.object(explorer, 'find_standard_concepts') as mock_find:
            mock_find.return_value = {
                'direct_matches': mock_search_result.all(),
                'synonym_matches': [],
                'relationship_matches': []
            }
            
            mappings = explorer.map_to_standard_concepts(
                query="test",
                target_vocabularies=["RxNorm"],  # Different from SNOMED in test data
                confidence_threshold=0.1
            )
            
            # Should filter out SNOMED concepts when only RxNorm is requested
            assert len(mappings) == 0 