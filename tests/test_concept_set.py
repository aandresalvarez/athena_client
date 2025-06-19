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

    @pytest.mark.asyncio
    async def test_tier2_warning_on_no_descendants(self):
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

        assert result["metadata"]["status"] == "SUCCESS"
        assert "no descendants" in result["metadata"]["warnings"][0]

    @pytest.mark.asyncio
    async def test_tier3_recovery_success(self):
        explorer = Mock()
        concept_a = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        concept_b = Concept(
            id=2,
            name="B",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.NON_STANDARD,
            code="B",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept_a}, {"concept": concept_b}]
        )

        db = Mock()
        db.validate_concepts.side_effect = [[], [3]]
        db.get_standard_mapping.return_value = {2: 3}
        db.get_descendants.return_value = [4]

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test")

        assert set(result["concept_ids"]) == {3, 4}
        assert (
            result["metadata"]["strategy_used"] == "Tier 3: Recovery via Local Mapping"
        )
        assert "Recovered" in result["metadata"]["warnings"][0]

    @pytest.mark.asyncio
    async def test_tier3_recovery_fails_if_mapped_is_invalid(self):
        explorer = Mock()
        concept_a = Concept(
            id=1,
            name="A",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.STANDARD,
            code="A",
        )
        concept_b = Concept(
            id=2,
            name="B",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical",
            standardConcept=ConceptType.NON_STANDARD,
            code="B",
        )
        explorer.map_to_standard_concepts = AsyncMock(
            return_value=[{"concept": concept_a}, {"concept": concept_b}]
        )

        db = Mock()
        db.validate_concepts.side_effect = [[], []]
        db.get_standard_mapping.return_value = {2: 3}

        generator = ConceptSetGenerator(explorer, db)
        result = await generator.create_from_query("test")

        assert result["metadata"]["status"] == "FAILURE"

    @pytest.mark.asyncio
    async def test_strict_mode_skips_tier3_recovery(self):
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
        db.get_standard_mapping.assert_not_called()
