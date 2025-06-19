import json

import pytest

from athena_client.models import Concept, ConceptSearchResponse, ConceptType

SAMPLE = ConceptSearchResponse(
    content=[
        Concept(
            id=i,
            name=f"Name {i}",
            domain="Domain",
            vocabulary="Vocab",
            className="Class",
            code=str(i),
            standardConcept=ConceptType.STANDARD,
            invalidReason=None,
            score=1.0,
        )
        for i in range(1000)
    ],
    pageable={
        "sort": {"sorted": True, "unsorted": False, "empty": False},
        "pageSize": 20,
        "pageNumber": 0,
        "offset": 0,
        "paged": True,
        "unpaged": False,
    },
    totalElements=1000,
    last=True,
    totalPages=1,
    first=True,
    sort={"sorted": True, "unsorted": False, "empty": False},
    size=1000,
    number=0,
    numberOfElements=1000,
    empty=False,
)


@pytest.mark.benchmark(group="json")
def test_orjson_dump(benchmark):
    benchmark(SAMPLE.model_dump_json)


@pytest.mark.benchmark(group="json")
def test_stdlib_dump(benchmark):
    benchmark(json.dumps, SAMPLE.model_dump())
