import json

import pytest

from athena_client.models import Concept, ConceptSearchResponse

SAMPLE = ConceptSearchResponse(
    content=[
        Concept(
            id=i,
            name=f"Name {i}",
            domain_id="D",
            vocabulary_id="V",
            concept_class_id="C",
            concept_code=str(i),
            invalid_reason=None,
            domain={"id": 1, "name": "Domain"},
            vocabulary={"id": "V", "name": "Vocab"},
            concept_class={"id": "C", "name": "Class"},
            valid_start_date="2020-01-01",
            valid_end_date="2099-01-01",
            standard_concept=None,
        )
        for i in range(1000)
    ],
    pageable={},
    total_elements=1000,
    last=True,
    total_pages=1,
    sort={},
    first=True,
    size=1000,
    number=0,
    number_of_elements=1000,
    empty=False,
)


@pytest.mark.benchmark(group="json")
def test_orjson_dump(benchmark):
    benchmark(SAMPLE.model_dump_json)


@pytest.mark.benchmark(group="json")
def test_stdlib_dump(benchmark):
    benchmark(json.dumps, SAMPLE.model_dump())
