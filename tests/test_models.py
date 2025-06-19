"""
Tests for Pydantic models and data validation.
"""

import pytest

from athena_client.models import (
    Concept,
    ConceptDetails,
    ConceptSearchResponse,
    ConceptType,
)


class TestConceptType:
    """Test ConceptType enum."""

    def test_concept_type_values(self):
        """Test ConceptType enum values."""
        assert ConceptType.STANDARD == "Standard"
        assert ConceptType.NON_STANDARD == "Non-standard"
        assert ConceptType.CLASSIFICATION == "Classification"

    def test_concept_type_string_representation(self):
        """Test ConceptType string representation."""
        assert ConceptType.STANDARD == "Standard"
        assert ConceptType.NON_STANDARD == "Non-standard"
        assert ConceptType.CLASSIFICATION == "Classification"


class TestConcept:
    """Test Concept model."""

    def test_concept_initialization(self):
        """Test Concept model initialization."""
        concept = Concept(
            id=1,
            name="Aspirin",
            domain="Drug",
            vocabulary="RxNorm",
            className="Ingredient",
            standardConcept=ConceptType.STANDARD,
            code="1191",
            invalidReason=None,
            score=1.0,
        )

        assert concept.id == 1
        assert concept.name == "Aspirin"
        assert concept.domain == "Drug"
        assert concept.vocabulary == "RxNorm"
        assert concept.className == "Ingredient"
        assert concept.standardConcept == ConceptType.STANDARD
        assert concept.code == "1191"
        assert concept.invalidReason is None
        assert concept.score == 1.0

    def test_concept_from_dict(self):
        """Test Concept model creation from dictionary."""
        data = {
            "id": 1,
            "name": "Aspirin",
            "domain": "Drug",
            "vocabulary": "RxNorm",
            "className": "Ingredient",
            "standardConcept": "Standard",
            "code": "1191",
            "invalidReason": None,
            "score": 1.0,
        }

        concept = Concept.model_validate(data)

        assert concept.name == "Aspirin"
        assert concept.standardConcept == ConceptType.STANDARD

    def test_concept_with_optional_fields(self):
        """Test Concept model with optional fields."""
        concept_data = {
            "id": 1,
            "name": "Aspirin",
            "domain": "Drug",
            "vocabulary": "RxNorm",
            "className": "Ingredient",
            "standardConcept": None,
            "code": "1191",
            "invalidReason": "U",
            "score": 0.8,
        }

        concept = Concept.model_validate(concept_data)

        assert concept.id == 1
        assert concept.name == "Aspirin"
        assert concept.standardConcept is None
        assert concept.invalidReason == "U"
        assert concept.score == 0.8

    def test_concept_string_representation(self):
        """Test Concept string representation."""
        concept = Concept(
            id=1,
            name="Aspirin",
            domain="Drug",
            vocabulary="RxNorm",
            className="Ingredient",
            standardConcept=ConceptType.STANDARD,
            code="1191",
            invalidReason=None,
            score=1.0,
        )

        # Test that string representation includes key fields
        concept_str = str(concept)
        assert "Aspirin" in concept_str
        assert "Drug" in concept_str


class TestConceptDetails:
    """Test ConceptDetails model."""

    def test_concept_details_initialization(self):
        """Test ConceptDetails model initialization."""
        details = ConceptDetails(
            id=1,
            name="Aspirin",
            domainId="Drug",
            vocabularyId="RxNorm",
            conceptClassId="Ingredient",
            standardConcept=ConceptType.STANDARD,
            conceptCode="1191",
            invalidReason=None,
            validStart="2000-01-01",
            validEnd="2099-12-31",
        )

        assert details.id == 1
        assert details.name == "Aspirin"
        assert details.domainId == "Drug"
        assert details.vocabularyId == "RxNorm"
        assert details.conceptClassId == "Ingredient"
        assert details.standardConcept == ConceptType.STANDARD
        assert details.conceptCode == "1191"
        assert details.invalidReason is None
        assert details.validStart == "2000-01-01"
        assert details.validEnd == "2099-12-31"

    def test_concept_details_from_dict(self):
        """Test ConceptDetails model creation from dictionary."""
        data = {
            "id": 1,
            "name": "Aspirin",
            "domainId": "Drug",
            "vocabularyId": "RxNorm",
            "conceptClassId": "Ingredient",
            "standardConcept": "Standard",
            "conceptCode": "1191",
            "invalidReason": None,
            "validStart": "2000-01-01",
            "validEnd": "2099-12-31",
        }

        details = ConceptDetails.model_validate(data)

        assert details.name == "Aspirin"
        assert details.standardConcept == ConceptType.STANDARD

    def test_concept_details_without_optional_fields(self):
        """Test ConceptDetails model without optional fields."""
        details_data = {
            "id": 1,
            "name": "Aspirin",
            "domainId": "Drug",
            "vocabularyId": "RxNorm",
            "conceptClassId": "Ingredient",
            "standardConcept": "Standard",
            "conceptCode": "1191",
            "invalidReason": None,
            "validStart": "2000-01-01",
            "validEnd": "2099-12-31",
        }

        details = ConceptDetails.model_validate(details_data)

        assert details.id == 1
        assert details.name == "Aspirin"
        assert details.standardConcept == ConceptType.STANDARD

    def test_concept_details_string_representation(self):
        """Test ConceptDetails string representation."""
        details = ConceptDetails(
            id=1,
            name="Aspirin",
            domainId="Drug",
            vocabularyId="RxNorm",
            conceptClassId="Ingredient",
            standardConcept=ConceptType.STANDARD,
            conceptCode="1191",
            invalidReason=None,
            validStart="2000-01-01",
            validEnd="2099-12-31",
        )

        # Test that string representation includes key fields
        details_str = str(details)
        assert "Aspirin" in details_str
        assert "Drug" in details_str


class TestConceptSearchResponse:
    """Test ConceptSearchResponse model."""

    def test_concept_search_response_initialization(self):
        """Test ConceptSearchResponse model initialization."""
        response = ConceptSearchResponse(
            content=[
                Concept(
                    id=1,
                    name="Aspirin",
                    domain="Drug",
                    vocabulary="RxNorm",
                    className="Ingredient",
                    standardConcept=ConceptType.STANDARD,
                    code="1191",
                    invalidReason=None,
                    score=1.0,
                )
            ],
            pageable={"pageSize": 1},
            totalElements=1,
            last=True,
            totalPages=1,
            first=True,
            size=1,
            number=0,
            numberOfElements=1,
            empty=False,
        )

        assert len(response.content) == 1
        assert response.content[0].name == "Aspirin"
        assert response.totalElements == 1
        assert response.last is True
        assert response.empty is False

    def test_concept_search_response_from_dict(self):
        """Test ConceptSearchResponse model creation from dictionary."""
        data = {
            "content": [
                {
                    "id": 1,
                    "name": "Aspirin",
                    "domain": "Drug",
                    "vocabulary": "RxNorm",
                    "className": "Ingredient",
                    "standardConcept": "Standard",
                    "code": "1191",
                    "invalidReason": None,
                    "score": 1.0,
                }
            ],
            "pageable": {"pageSize": 1},
            "totalElements": 1,
            "last": True,
            "totalPages": 1,
            "first": True,
            "size": 1,
            "number": 0,
            "numberOfElements": 1,
            "empty": False,
        }

        response = ConceptSearchResponse.model_validate(data)

        assert len(response.content) == 1
        assert response.content[0].name == "Aspirin"
        assert response.totalElements == 1
        assert response.last is True
        assert response.empty is False

    def test_concept_search_response_empty(self):
        """Test ConceptSearchResponse model with empty results."""
        response_data = {
            "content": [],
            "pageable": {"pageSize": 1},
            "totalElements": 0,
            "last": True,
            "totalPages": 1,
            "first": True,
            "size": 1,
            "number": 0,
            "numberOfElements": 0,
            "empty": True,
        }

        response = ConceptSearchResponse.model_validate(response_data)

        assert len(response.content) == 0
        assert response.totalElements == 0
        assert response.empty is True


class TestModelValidation:
    """Test model validation and error handling."""

    def test_invalid_concept_data(self):
        """Test validation error with invalid concept data."""
        invalid_data = {
            "id": "not_an_integer",  # Should be int
            "name": "Aspirin",
            "domain_id": "Drug",
            "vocabulary_id": "RxNorm",
            "concept_class_id": "Ingredient",
            "standard_concept": "S",
            "concept_code": "1191",
            "valid_start_date": "2000-01-01",
            "valid_end_date": "2099-12-31",
            "invalid_reason": None,
            "domain": {"id": 13, "name": "Drug"},
            "vocabulary": {"id": "RxNorm", "name": "RxNorm"},
            "concept_class": {"id": "Ingredient", "name": "Ingredient"},
        }

        with pytest.raises(ValueError):
            Concept.model_validate(invalid_data)

    def test_missing_required_fields(self):
        """Test validation error with missing required fields."""
        incomplete_data = {
            "id": 1127433,
            "name": "Aspirin",
            # Missing required fields
        }

        with pytest.raises(ValueError):
            Concept.model_validate(incomplete_data)

    def test_invalid_concept_type(self):
        """Test validation error with invalid concept type."""
        invalid_data = {
            "id": 1127433,
            "name": "Aspirin",
            "domain_id": "Drug",
            "vocabulary_id": "RxNorm",
            "concept_class_id": "Ingredient",
            "standard_concept": "INVALID",  # Invalid enum value
            "concept_code": "1191",
            "valid_start_date": "2000-01-01",
            "valid_end_date": "2099-12-31",
            "invalid_reason": None,
            "domain": {"id": 13, "name": "Drug"},
            "vocabulary": {"id": "RxNorm", "name": "RxNorm"},
            "concept_class": {"id": "Ingredient", "name": "Ingredient"},
        }

        with pytest.raises(ValueError):
            Concept.model_validate(invalid_data)
