"""
Tests for the Query DSL.
"""

from athena_client.query import Q


def test_term_query():
    """Test basic term query construction."""
    q = Q.term("diabetes")
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == "diabetes"
    assert "name^10" in boosts["filter"]["query_string"]["fields"]
    assert "synonyms^5" in boosts["filter"]["query_string"]["fields"]


def test_phrase_query():
    """Test phrase query construction."""
    q = Q.phrase("heart attack")
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == '"heart attack"'


def test_exact_query():
    """Test exact query construction."""
    q = Q.exact('"Myocardial Infarction"')
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == '"Myocardial Infarction"'
    assert "concept_code^20" in boosts["filter"]["query_string"]["fields"]
    assert "name.exact^15" in boosts["filter"]["query_string"]["fields"]


def test_wildcard_query():
    """Test wildcard query construction."""
    q = Q.wildcard("aspir*")
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["query"] == "aspir*"


def test_fuzzy_modifier():
    """Test fuzzy modifier."""
    q = Q.term("aspirin").fuzzy(0.8)
    boosts = q.to_boosts()

    assert boosts["filter"]["query_string"]["fuzziness"] == 0.8


def test_and_operator():
    """Test AND operator."""
    q = Q.term("diabetes") & Q.term("type 2")
    boosts = q.to_boosts()

    assert "must" in boosts["filter"]["bool"]
    assert len(boosts["filter"]["bool"]["must"]) == 2


def test_or_operator():
    """Test OR operator."""
    q = Q.term("heart") | Q.term("cardiac")
    boosts = q.to_boosts()

    assert "should" in boosts["filter"]["bool"]
    assert len(boosts["filter"]["bool"]["should"]) == 2


def test_not_operator():
    """Test NOT operator."""
    q = -Q.term("chronic")
    boosts = q.to_boosts()

    assert "must_not" in boosts["filter"]["bool"]
    assert len(boosts["filter"]["bool"]["must_not"]) == 1


def test_complex_query():
    """Test complex query with multiple operators."""
    q = (Q.term("diabetes") & Q.term("type 2")) | Q.exact('"diabetic nephropathy"')
    boosts = q.to_boosts()

    assert "should" in boosts["filter"]["bool"]
