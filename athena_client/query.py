"""
Query DSL for building complex Athena queries.

This module provides a Query DSL that allows for building complex queries
using a fluent interface and operator overloading.
"""

from typing import Any, Dict, Optional


class Q:
    """
    Query DSL for building complex Athena queries.

    Usage:
        q = Q.term("diabetes")
        q = Q.phrase("heart attack")
        q = Q.exact('"Myocardial Infarction"')
        q = Q.wildcard("aspir*")

        # Combine with operators
        q = Q.term("diabetes") & Q.term("type 2")  # AND
        q = Q.term("heart") | Q.term("cardiac")    # OR
        q = -Q.term("chronic")                     # NOT

        # Apply modifiers
        q = Q.term("aspirin").fuzzy(0.8)

        # Get boosts for the API
        boosts = q.to_boosts()
    """

    def __init__(self, query_type: str, value: str, **kwargs: Any) -> None:
        """
        Initialize a query object.

        Args:
            query_type: Type of query (term, phrase, exact, wildcard)
            value: Query value
            **kwargs: Additional options
        """
        self.query_type = query_type
        self.value = value
        self.options = kwargs
        self.operator: Optional[str] = None
        self.left: Optional["Q"] = None
        self.right: Optional["Q"] = None

    @classmethod
    def term(cls, value: str) -> "Q":
        """
        Create a term query.

        Args:
            value: Term to search for

        Returns:
            Query object
        """
        return cls("term", value)

    @classmethod
    def phrase(cls, value: str) -> "Q":
        """
        Create a phrase query.

        Args:
            value: Phrase to search for

        Returns:
            Query object
        """
        return cls("phrase", value)

    @classmethod
    def exact(cls, value: str) -> "Q":
        """
        Create an exact match query.

        Args:
            value: Exact phrase to search for (should be in quotes)

        Returns:
            Query object
        """
        if not value.startswith('"') or not value.endswith('"'):
            value = f'"{value}"'
        return cls("exact", value)

    @classmethod
    def wildcard(cls, value: str) -> "Q":
        """
        Create a wildcard query.

        Args:
            value: Wildcard pattern (e.g., "aspir*")

        Returns:
            Query object
        """
        if not value.endswith("*"):
            value = f"{value}*"
        return cls("wildcard", value)

    def fuzzy(self, ratio: float = 0.7) -> "Q":
        """
        Apply fuzzy matching to the query.

        Args:
            ratio: Fuzzy match ratio (0.0 - 1.0)

        Returns:
            Query object with fuzzy matching
        """
        self.options["fuzzy"] = ratio
        return self

    def __and__(self, other: "Q") -> "Q":
        """
        Combine with AND operator.

        Args:
            other: Another Q object

        Returns:
            New Q object representing the AND condition
        """
        result = Q("compound", "")
        result.operator = "AND"
        result.left = self
        result.right = other
        return result

    def __or__(self, other: "Q") -> "Q":
        """
        Combine with OR operator.

        Args:
            other: Another Q object

        Returns:
            New Q object representing the OR condition
        """
        result = Q("compound", "")
        result.operator = "OR"
        result.left = self
        result.right = other
        return result

    def __neg__(self) -> "Q":
        """
        Apply NOT operator.

        Returns:
            New Q object representing the NOT condition
        """
        result = Q("compound", "")
        result.operator = "NOT"
        result.right = self
        return result

    def to_boosts(self) -> Dict[str, Any]:
        """
        Convert the query to a boosts dictionary for the Athena API.

        Returns:
            Dictionary with query boosts
        """
        if self.query_type == "compound":
            if self.operator == "AND":
                assert self.left is not None and self.right is not None
                boosts_left = self.left.to_boosts()
                boosts_right = self.right.to_boosts()
                # Merge the boosts with AND logic
                return {
                    "filter": {
                        "bool": {
                            "must": [
                                boosts_left.get("filter", {}),
                                boosts_right.get("filter", {}),
                            ]
                        }
                    }
                }
            elif self.operator == "OR":
                assert self.left is not None and self.right is not None
                boosts_left = self.left.to_boosts()
                boosts_right = self.right.to_boosts()
                # Merge the boosts with OR logic
                return {
                    "filter": {
                        "bool": {
                            "should": [
                                boosts_left.get("filter", {}),
                                boosts_right.get("filter", {}),
                            ]
                        }
                    }
                }
            elif self.operator == "NOT":
                assert self.right is not None
                boosts_right = self.right.to_boosts()
                # Apply NOT logic
                return {
                    "filter": {"bool": {"must_not": [boosts_right.get("filter", {})]}}
                }
            # Fallback for unrecognized operator
            return {"filter": {"query_string": {"query": self.value}}}

        # Handle basic query types
        query_dict: Dict[str, Any] = {}

        if self.query_type == "term":
            query_dict["query"] = self.value
            query_dict["fields"] = [
                "name^10",
                "synonyms^5",
                "definition^3",
                "concept_code",
            ]
        elif self.query_type == "phrase":
            query_dict["query"] = f'"{self.value}"'
            query_dict["fields"] = ["name^10", "synonyms^5", "definition^3"]
        elif self.query_type == "exact":
            query_dict["query"] = self.value
            query_dict["fields"] = ["concept_code^20", "name.exact^15"]
        elif self.query_type == "wildcard":
            query_dict["query"] = self.value
            query_dict["fields"] = ["name^10", "synonyms^5"]

        # Apply fuzzy if requested
        if "fuzzy" in self.options:
            query_dict["fuzziness"] = self.options["fuzzy"]

        if query_dict:
            return {"filter": {"query_string": query_dict}}
        # Final fallback for unhandled query types
        return {"filter": {"query_string": {"query": self.value}}}

    def __str__(self) -> str:
        """
        Convert the query to a string representation for API calls.

        Returns:
            String representation of the query
        """
        if self.query_type == "compound":
            if self.operator == "AND":
                assert self.left is not None and self.right is not None
                return f"({self.left}) AND ({self.right})"
            elif self.operator == "OR":
                assert self.left is not None and self.right is not None
                return f"({self.left}) OR ({self.right})"
            elif self.operator == "NOT":
                assert self.right is not None
                return f"NOT ({self.right})"
            # Gracefully handle unknown operators by returning the raw value
            return self.value
        else:
            # For basic query types, return the value
            return self.value
