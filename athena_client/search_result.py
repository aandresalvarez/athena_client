"""
SearchResult formatter for Athena search results.

This module provides a class for handling and formatting search results
from the Athena API into various output formats.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel

from .exceptions import ValidationError
from .models import Concept, ConceptSearchResponse


class SearchResult:
    """
    Formatter for search results from the Athena API.
    
    This class provides methods to convert search results into various formats:
    - Pydantic models (all, top)
    - Python dictionaries (to_list)
    - pandas DataFrames (to_df)
    - JSON (to_json)
    - YAML (to_yaml)
    - CSV (to_csv)
    """
    
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize with API response data.
        
        Args:
            data: Raw API response from search endpoint
            
        Raises:
            ValidationError: If the data cannot be parsed
        """
        try:
            self._response = ConceptSearchResponse.model_validate(data)
        except Exception as e:
            raise ValidationError(f"Failed to parse search results: {e}") from e
    
    def all(self) -> List[Concept]:
        """
        Get all concepts as Pydantic objects.
        
        Returns:
            List of Concept objects
        """
        return self._response.content
    
    def top(self, n: int = 10) -> List[Concept]:
        """
        Get top N concepts as Pydantic objects.
        
        Args:
            n: Number of concepts to return
            
        Returns:
            List of top N Concept objects
        """
        return self._response.content[:n]
    
    def to_models(self) -> List[Concept]:
        """
        Alias for all().
        
        Returns:
            List of Concept objects
        """
        return self.all()
    
    def to_list(self) -> List[Dict[str, Any]]:
        """
        Get concepts as list of dictionaries.
        
        Returns:
            List of concept dictionaries
        """
        return [concept.model_dump() for concept in self.all()]
    
    def to_df(self) -> Any:
        """
        Get concepts as pandas DataFrame.
        
        Returns:
            pandas DataFrame
            
        Raises:
            ImportError: If pandas is not installed
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for DataFrame output. "
                "Install with 'pip install \"athena-client[pandas]\"'"
            )
        
        return pd.DataFrame(self.to_list())
    
    def to_json(self, indent: int = 2) -> str:
        """
        Get concepts as JSON string.
        
        Args:
            indent: Indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(self.to_list(), indent=indent)
    
    def to_yaml(self) -> str:
        """
        Get concepts as YAML string.
        
        Returns:
            YAML string
            
        Raises:
            ImportError: If PyYAML is not installed
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML output. "
                "Install with 'pip install \"athena-client[yaml]\"'"
            )
            
        return yaml.dump(self.to_list())
    
    def to_csv(self, path: Union[str, Path]) -> None:
        """
        Write concepts to CSV file.
        
        Args:
            path: File path to write CSV to
            
        Raises:
            ImportError: If pandas is not installed
        """
        df = self.to_df()  # This will raise ImportError if pandas is missing
        df.to_csv(path, index=False)
    
    def __len__(self) -> int:
        """
        Get the number of results.
        
        Returns:
            Number of concepts
        """
        return len(self._response.content)
    
    def __getitem__(self, idx: int) -> Concept:
        """
        Get a specific concept by index.
        
        Args:
            idx: Index of the concept
            
        Returns:
            Concept at the given index
        """
        return self._response.content[idx]
    
    @property
    def total(self) -> int:
        """
        Get the total number of results.
        
        Returns:
            Total number of results
        """
        return self._response.total_elements
    
    @property
    def page(self) -> int:
        """
        Get the current page number.
        
        Returns:
            Current page number
        """
        return self._response.number
    
    @property
    def pages(self) -> int:
        """
        Get the total number of pages.
        
        Returns:
            Total number of pages
        """
        return self._response.total_pages
