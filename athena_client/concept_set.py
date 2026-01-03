import logging
from typing import Any, Dict, List, Optional

from .concept_explorer import ConceptExplorer
from .db.base import DatabaseConnector

logger = logging.getLogger(__name__)


class ConceptSetGenerator:
    """Orchestrate concept set generation from a search query."""

    def __init__(self, explorer: ConceptExplorer, db: DatabaseConnector) -> None:
        self.explorer = explorer
        self.db = db

    async def create_from_query(
        self,
        query: str,
        strategy: str = "fallback",
        include_descendants: bool = True,
        confidence_threshold: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate a concept set using a tiered standard-first strategy.
        Includes robust error handling.
        """
        from .exceptions import AthenaError

        try:
            logger.info(
                "Attempting to find and validate standard concepts for query: '%s'",
                query,
            )
            mappings = await self.explorer.map_to_standard_concepts(
                query, confidence_threshold=confidence_threshold, **kwargs
            )

            from .models import ConceptType

            standard_concepts = [
                m["concept"]
                for m in mappings
                if m["concept"].standardConcept == ConceptType.STANDARD
            ]

            if standard_concepts:
                candidate_ids = [c.id for c in standard_concepts]
                validated_ids = self.db.validate_concepts(candidate_ids)

                if validated_ids:
                    warnings: List[str] = []
                    final_ids = set(validated_ids)
                    if include_descendants:
                        desc_ids = self.db.get_descendants(validated_ids)
                        if not desc_ids:
                            warnings.append(
                                (
                                    f"Standard concepts {validated_ids} found but "
                                    "have no descendants in the local vocabulary."
                                )
                            )
                        else:
                            final_ids.update(desc_ids)

                    return self._build_success_response(
                        query=query,
                        strategy_used="Tier 1: Direct Standard Concept",
                        concept_ids=list(final_ids),
                        seed_concepts=validated_ids,
                        warnings=warnings,
                    )

            if strategy == "strict":
                return self._build_failure_response(
                    query,
                    (
                        "No standard concepts from the API could be validated in "
                        "'strict' mode."
                    ),
                )

            non_standard_concepts = [
                m["concept"]
                for m in mappings
                if m["concept"].standardConcept != ConceptType.STANDARD
            ]

            if non_standard_concepts:
                local_mappings = self.db.get_standard_mapping(
                    [c.id for c in non_standard_concepts]
                )
                if local_mappings:
                    # Collect all standard IDs from all mappings
                    all_mapped_standard_ids = []
                    for mapped_ids in local_mappings.values():
                        all_mapped_standard_ids.extend(mapped_ids)
                    
                    validated_ids = self.db.validate_concepts(all_mapped_standard_ids)
                    if validated_ids:
                        final_ids = set(validated_ids)
                        if include_descendants:
                            final_ids.update(self.db.get_descendants(validated_ids))
                        
                        source_ids = list(local_mappings.keys())
                        warnings = []
                        warning = (
                            "Initial standard concepts not found locally. "
                            "Recovered by mapping non-standard concepts "
                            f"{source_ids[:5]}{'...' if len(source_ids) > 5 else ''} "
                            "to their standard equivalents."
                        )
                        warnings.append(warning)
                        
                        # Add warning if some mapped concepts failed local validation
                        if len(validated_ids) < len(all_mapped_standard_ids):
                            missing_count = len(all_mapped_standard_ids) - len(validated_ids)
                            warnings.append(
                                f"Caution: {missing_count} standard concepts found via mapping "
                                "are missing from the local database and were excluded."
                            )
                            
                        return self._build_success_response(
                            query=query,
                            strategy_used="Tier 3: Recovery via Local Mapping",
                            concept_ids=list(final_ids),
                            seed_concepts=validated_ids,
                            warnings=warnings,
                        )
                    elif all_mapped_standard_ids:
                        # Standard IDs were found via mapping but failed local validation
                        logger.warning(
                            "Mapping found standard IDs %s but none were valid in local DB.",
                            all_mapped_standard_ids[:10],
                        )
                        return self._build_failure_response(
                            query,
                            (
                                f"Standard concepts {all_mapped_standard_ids[:5]} found "
                                "via mapping but are missing from the local database."
                            ),
                        )

            return self._build_failure_response(
                query,
                (
                    "No standard concepts from the API could be validated against "
                    "the local database, and no recovery paths were found."
                ),
            )
        except AthenaError as err:
            logger.error(f"Athena client error during concept set generation: {err}")
            # Return a structured failure response with troubleshooting info
            return {
                "name": f"Failed Concept Set for '{query}'",
                "concept_ids": [],
                "metadata": {
                    "status": "FAILURE",
                    "source_query": query,
                    "reason": str(err),
                    "suggestions": [
                        "Check your network connection and credentials.",
                        "Try again in a few moments.",
                        getattr(err, "troubleshooting", None)
                        or "See logs for more details.",
                    ],
                },
            }

    def _build_success_response(
        self,
        query: str,
        strategy_used: str,
        concept_ids: List[int],
        seed_concepts: List[int],
        warnings: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "name": f"Concept Set for '{query}'",
            "concept_ids": concept_ids,
            "metadata": {
                "status": "SUCCESS",
                "strategy_used": strategy_used,
                "source_query": query,
                "seed_concepts": seed_concepts,
                "warnings": warnings or [],
            },
        }

    def _build_failure_response(self, query: str, reason: str) -> Dict[str, Any]:
        return {
            "name": f"Failed Concept Set for '{query}'",
            "concept_ids": [],
            "metadata": {
                "status": "FAILURE",
                "source_query": query,
                "reason": reason,
                "suggestions": [
                    "Try a different search term.",
                    "Lower the `confidence_threshold`.",
                    "Check if your local vocabulary version is up to date.",
                ],
            },
        }
