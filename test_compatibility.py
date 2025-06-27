#!/usr/bin/env python3
"""
Simple compatibility test for athena-client.

This script tests that the library works with the current dependency versions.
"""

import sys
import importlib

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing imports...")
    
    try:
        from athena_client import Athena, AthenaClient
        print("✅ Core client imports successful")
    except ImportError as e:
        print(f"❌ Core client import failed: {e}")
        assert False, f"Core client import failed: {e}"
    
    try:
        from athena_client.models import Concept, ConceptDetails
        print("✅ Model imports successful")
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        assert False, f"Model import failed: {e}"
    
    try:
        from athena_client.query import Q
        print("✅ Query DSL imports successful")
    except ImportError as e:
        print(f"❌ Query DSL import failed: {e}")
        assert False, f"Query DSL import failed: {e}"
    
    try:
        from athena_client.db.sqlalchemy_connector import SQLAlchemyConnector
        print("✅ SQLAlchemy connector imports successful")
    except ImportError as e:
        print(f"❌ SQLAlchemy connector import failed: {e}")
        assert False, f"SQLAlchemy connector import failed: {e}"


def test_dependency_versions():
    """Test dependency versions."""
    print("\nTesting dependency versions...")
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
        assert sqlalchemy.__version__.startswith(("2.", "1.4")), (
            f"Unsupported SQLAlchemy version: {sqlalchemy.__version__}"
        )
    except ImportError:
        print("❌ SQLAlchemy not installed")
        assert False, "SQLAlchemy not installed"
    
    try:
        import pandas
        print(f"✅ pandas version: {pandas.__version__}")
    except ImportError:
        print("❌ pandas not installed")
        assert False, "pandas not installed"
    
    try:
        import pydantic
        print(f"✅ pydantic version: {pydantic.__version__}")
        assert pydantic.__version__.startswith("2."), (
            f"Unsupported pydantic version: {pydantic.__version__}"
        )
    except ImportError:
        print("❌ pydantic not installed")
        assert False, "pydantic not installed"
    
    try:
        import httpx
        print(f"✅ httpx version: {httpx.__version__}")
    except ImportError:
        print("❌ httpx not installed")
        assert False, "httpx not installed"

def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from athena_client import Athena
        
        # Create client
        client = Athena()
        print("✅ Client creation successful")
        
        # Test query DSL
        from athena_client.query import Q
        query = Q.term("aspirin")
        print("✅ Query DSL creation successful")
        
        # Test model creation
        from athena_client.models import Concept
        concept = Concept(
            id=12345,
            name="Test Concept",
            domain="Condition",
            vocabulary="SNOMED",
            className="Clinical Finding",
            standardConcept="Standard",
            code="12345",
            invalidReason=None
        )
        print("✅ Model creation successful")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        assert False, f"Basic functionality test failed: {e}" 