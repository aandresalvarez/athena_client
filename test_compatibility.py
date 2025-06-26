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
        return False
    
    try:
        from athena_client.models import Concept, ConceptDetails
        print("✅ Model imports successful")
    except ImportError as e:
        print(f"❌ Model import failed: {e}")
        return False
    
    try:
        from athena_client.query import Q
        print("✅ Query DSL imports successful")
    except ImportError as e:
        print(f"❌ Query DSL import failed: {e}")
        return False
    
    try:
        from athena_client.db.sqlalchemy_connector import SQLAlchemyConnector
        print("✅ SQLAlchemy connector imports successful")
    except ImportError as e:
        print(f"❌ SQLAlchemy connector import failed: {e}")
        return False
    
    return True

def test_dependency_versions():
    """Test dependency versions."""
    print("\nTesting dependency versions...")
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
        if sqlalchemy.__version__.startswith('2.'):
            print("   → SQLAlchemy 2.x detected (modern version)")
        elif sqlalchemy.__version__.startswith('1.4'):
            print("   → SQLAlchemy 1.4.x detected (compatible version)")
        else:
            print(f"   → SQLAlchemy {sqlalchemy.__version__} detected")
    except ImportError:
        print("❌ SQLAlchemy not installed")
    
    try:
        import pandas
        print(f"✅ pandas version: {pandas.__version__}")
    except ImportError:
        print("❌ pandas not installed")
    
    try:
        import pydantic
        print(f"✅ pydantic version: {pydantic.__version__}")
        if pydantic.__version__.startswith('2.'):
            print("   → Pydantic 2.x detected (modern version)")
        else:
            print(f"   → Pydantic {pydantic.__version__} detected")
    except ImportError:
        print("❌ pydantic not installed")
    
    try:
        import httpx
        print(f"✅ httpx version: {httpx.__version__}")
    except ImportError:
        print("❌ httpx not installed")

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
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all compatibility tests."""
    print("🚀 Athena Client Compatibility Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test dependency versions
    test_dependency_versions()
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All compatibility tests passed!")
        print("   The library should work with current dependency versions.")
    else:
        print("❌ Some compatibility tests failed.")
        print("   Please check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 