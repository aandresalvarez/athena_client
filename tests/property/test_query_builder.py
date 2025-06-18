from hypothesis import given
from hypothesis import strategies as st

from athena_client.query import Q


@given(text=st.text(min_size=1, max_size=40))
def test_phrase_builder_roundtrip(text):
    """Generated boosts should always include the raw phrase."""
    boosts = Q.phrase(text).to_boosts()
    assert text in boosts["filter"]["query_string"]["query"]


@given(prefix=st.text(min_size=1, max_size=10))
def test_wildcard_always_star(prefix):
    """Wildcard helper must append '*' if caller forgot."""
    expr = Q.wildcard(prefix)
    assert expr.value.endswith("*")
