from unittest.mock import AsyncMock, Mock

import pytest

from athena_client.concept_set import ConceptSetGenerator
from athena_client.models import Concept, ConceptType


class TestConceptSetGenerator:
    @pytest.mark.asyncio
    async def test_tier1_happy_path(self):
        explorer = Mock()
        concept = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept}]
        )

        db = Mock()
        db.validate_concepts.return_value = [1]
        db.get_descendants.return_value = [2, 3]

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test")

        assert set(result["concept_ids"]) == {1, 2, 3}
        assert result["metadata"]["status"] == "SUCCESS"
        assert "Tier 1" in result["metadata"]["strategy_used"]

    @pytest.mark.asyncio
    async def test_tier1_no_descendants(self):
        explorer = Mock()
        concept = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept}]
        )

        db = Mock()
        db.validate_concepts.return_value = [1]
        db.get_descendants.return_value = []

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test")

        assert result["concept_ids"] == [1]
        assert result["metadata"]["status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_tier1_api_concept_not_in_local_db(self):
        explorer = Mock()
        concept = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept}]
        )

        db = Mock()
        db.validate_concepts.return_value = []

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test")

        assert result["metadata"]["status"] == "FAILURE"

    @pytest.mark.asyncio
    async def test_strict_strategy_failure(self):
        explorer = Mock()
        concept = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept}]
        )

        db = Mock()
        db.validate_concepts.return_value = []

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test", strategy="strict")

        assert result["metadata"]["status"] == "FAILURE"

    @pytest.mark.asyncio
    async def test_include_descendants_false(self):
        explorer = Mock()
        concept = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept}]
        )

        db = Mock()
        db.validate_concepts.return_value = [1]
        db.get_descendants.return_value = [2]

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test", include_descendants=False)

        assert result["concept_ids"] == [1]
        assert result["metadata"]["status"] == "SUCCESS"
