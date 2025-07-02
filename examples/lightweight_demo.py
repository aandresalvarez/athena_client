#!/usr/bin/env python3
"""
Lightweight Installation Demo

This script demonstrates the core functionality available with the lightweight installation:
pip install athena-client

This shows what works with only the 5 essential dependencies (~2MB) and what requires
additional optional dependencies.

Usage:
    python examples/lightweight_demo.py
"""

import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.query import Q


def main():
    print("🚀 ATHENA-CLIENT LIGHTWEIGHT INSTALLATION DEMO")
    print("=" * 60)
    print("This demo shows what works with: pip install athena-client")
    print("(Only 5 packages, ~2MB)")
    print("=" * 60)

    # Create client
    print("\n🔧 Creating Athena client...")
    athena = Athena()
    print("✅ Client created successfully")

    print("\n" + "=" * 60)
    print("1. CORE FUNCTIONALITY (Always Available)")
    print("=" * 60)

    # Basic search
    print("\n🔍 Basic search...")
    try:
        results = athena.search("aspirin", size=3)
        print(f"✅ Search successful! Found {len(results.all())} results")
        
        for i, concept in enumerate(results.all(), 1):
            print(f"  {i}. [{concept.id}] {concept.name}")
            print(f"     Domain: {concept.domain}")
            print(f"     Vocabulary: {concept.vocabulary}")
            print()
    except Exception as e:
        print(f"❌ Search failed: {e}")

    # Query DSL
    print("\n🔍 Query DSL search...")
    try:
        query = Q.term("heart") | Q.term("cardiac")
        complex_results = athena.search(query, size=2)
        print(f"✅ Query DSL successful! Found {len(complex_results.all())} results")
    except Exception as e:
        print(f"❌ Query DSL failed: {e}")

    # Result methods
    print("\n📊 Result methods...")
    try:
        results = athena.search("diabetes", size=2)
        
        # Core methods (always available)
        print(f"✅ .all(): {len(results.all())} concepts")
        print(f"✅ .top(1): {len(results.top(1))} concepts")
        print(f"✅ .to_list(): {len(results.to_list())} items")
        print(f"✅ .to_json(): {len(results.to_json())} characters")
        
        # Pagination info
        print(f"✅ Total elements: {results.total_elements}")
        print(f"✅ Current page: {results.current_page}")
        print(f"✅ Page size: {results.page_size}")
        
    except Exception as e:
        print(f"❌ Result methods failed: {e}")

    # Concept details
    print("\n🔍 Concept details...")
    try:
        if results.all():
            concept_id = results.all()[0].id
            details = athena.details(concept_id)
            print(f"✅ Concept details: {details.name}")
            print(f"   Domain: {details.domainId}")
            print(f"   Vocabulary: {details.vocabularyId}")
    except Exception as e:
        print(f"❌ Concept details failed: {e}")

    # Relationships
    print("\n🔗 Concept relationships...")
    try:
        if results.all():
            concept_id = results.all()[0].id
            relationships = athena.relationships(concept_id)
            print(f"✅ Relationships: {relationships.count} total")
    except Exception as e:
        print(f"❌ Relationships failed: {e}")

    # Graph
    print("\n🕸️ Concept graph...")
    try:
        if results.all():
            concept_id = results.all()[0].id
            graph = athena.graph(concept_id, depth=1)
            print(f"✅ Graph: {len(graph.terms)} terms, {len(graph.links)} links")
    except Exception as e:
        print(f"❌ Graph failed: {e}")

    print("\n" + "=" * 60)
    print("2. OPTIONAL FEATURES (Require Additional Installation)")
    print("=" * 60)

    # Test pandas DataFrame support
    print("\n📊 pandas DataFrame support...")
    try:
        df = results.to_df()
        print(f"✅ .to_df() works! DataFrame with {len(df)} rows")
        print("   (pandas is installed in this environment)")
    except ImportError:
        print("❌ .to_df() requires: pip install 'athena-client[pandas]'")
    except Exception as e:
        print(f"❌ .to_df() failed: {e}")

    # Test CLI availability
    print("\n💻 CLI availability...")
    try:
        from athena_client.cli import main
        print("✅ CLI module available")
        print("   (click and rich are installed in this environment)")
    except ImportError as e:
        if "click" in str(e):
            print("❌ CLI requires: pip install 'athena-client[cli]'")
        else:
            print(f"❌ CLI import failed: {e}")

    # Test YAML support
    print("\n📄 YAML support...")
    try:
        import yaml
        print("✅ YAML module available")
        print("   (pyyaml is installed in this environment)")
    except ImportError:
        print("❌ YAML support requires: pip install 'athena-client[yaml]'")

    # Test cryptography support
    print("\n🔐 HMAC authentication...")
    try:
        from athena_client.auth import build_headers
        print("✅ Auth module available")
        print("   (cryptography is installed in this environment)")
    except ImportError as e:
        if "cryptography" in str(e):
            print("❌ HMAC auth requires: pip install 'athena-client[crypto]'")
        else:
            print(f"❌ Auth import failed: {e}")

    # Test database support
    print("\n🗄️ Database support...")
    try:
        from athena_client.db.sqlalchemy_connector import SQLAlchemyConnector
        print("✅ Database connector available")
        print("   (sqlalchemy and psycopg2 are installed in this environment)")
    except ImportError as e:
        if "sqlalchemy" in str(e):
            print("❌ Database support requires: pip install 'athena-client[db]'")
        else:
            print(f"❌ Database import failed: {e}")

    print("\n" + "=" * 60)
    print("3. INSTALLATION RECOMMENDATIONS")
    print("=" * 60)

    print("\n📦 Installation Options:")
    print("  Minimal (recommended):")
    print("    pip install athena-client")
    print("    # 5 packages, ~2MB - Core API functionality only")
    
    print("\n  Individual features:")
    print("    pip install 'athena-client[cli]'      # +2 packages, +3MB")
    print("    pip install 'athena-client[pandas]'   # +1 package, +15MB")
    print("    pip install 'athena-client[yaml]'     # +1 package, +1MB")
    print("    pip install 'athena-client[crypto]'   # +1 package, +4MB")
    print("    pip install 'athena-client[db]'       # +2 packages, +3MB")
    
    print("\n  Full installation:")
    print("    pip install 'athena-client[full]'")
    print("    # 11 packages, ~25MB - All features")

    print("\n" + "=" * 60)
    print("🎉 LIGHTWEIGHT DEMO COMPLETED!")
    print("=" * 60)
    print("\n✅ Core functionality works with minimal dependencies")
    print("✅ Optional features are properly handled")
    print("✅ Users can choose what to install")
    print("\n💡 This approach provides:")
    print("   - Faster installation")
    print("   - Smaller footprint")
    print("   - Fewer dependency conflicts")
    print("   - Clear feature separation")


if __name__ == "__main__":
    main() 