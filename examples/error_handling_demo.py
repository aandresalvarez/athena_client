#!/usr/bin/env python3
"""
Comprehensive demo showcasing the enhanced error handling system.

This demo demonstrates how the athena-client provides clear, actionable error messages
for various failure scenarios, helping users understand and resolve issues quickly.
"""
import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.exceptions import (
    AthenaError, NetworkError, TimeoutError, ClientError, ServerError,
    AuthenticationError, RateLimitError, ValidationError, APIError
)


def demo_network_errors():
    """Demonstrate network error handling."""
    print("\n🌐 NETWORK ERROR HANDLING")
    print("=" * 50)
    
    print("\n1. DNS Resolution Failure:")
    print("-" * 30)
    try:
        client = Athena(base_url="https://invalid-domain-that-does-not-exist-12345.com/api/v1")
        client.search("aspirin")
    except Exception as e:
        print(f"✅ Error Type: {type(e).__name__}")
        print(f"✅ Error Message: {e}")
    
    print("\n2. Connection Timeout:")
    print("-" * 30)
    try:
        client = Athena(timeout=0.001)  # Very short timeout
        client.search("aspirin")
    except Exception as e:
        print(f"✅ Error Type: {type(e).__name__}")
        print(f"✅ Error Message: {e}")


def demo_api_errors():
    """Demonstrate API error handling."""
    print("\n🔌 API ERROR HANDLING")
    print("=" * 50)
    
    client = Athena()
    
    print("\n1. Invalid Concept ID:")
    print("-" * 30)
    try:
        client.details(999999999)  # Non-existent concept ID
    except Exception as e:
        print(f"✅ Error Type: {type(e).__name__}")
        print(f"✅ Error Message: {e}")
    
    print("\n2. Invalid Search Parameters:")
    print("-" * 30)
    try:
        client.search("", page=0, size=0)  # Invalid page size
    except Exception as e:
        print(f"✅ Error Type: {type(e).__name__}")
        print(f"✅ Error Message: {e}")
    
    print("\n3. Empty Search Query:")
    print("-" * 30)
    try:
        client.search("")  # Empty query
    except Exception as e:
        print(f"✅ Error Type: {type(e).__name__}")
        print(f"✅ Error Message: {e}")


def demo_http_errors():
    """Demonstrate HTTP error handling."""
    print("\n🌍 HTTP ERROR HANDLING")
    print("=" * 50)
    
    client = Athena()
    
    print("\n1. 404 Not Found:")
    print("-" * 30)
    try:
        client.http.get("/nonexistent-endpoint")
    except Exception as e:
        print(f"✅ Error Type: {type(e).__name__}")
        print(f"✅ Error Message: {e}")


def demo_error_recovery():
    """Demonstrate error recovery and retry behavior."""
    print("\n🔄 ERROR RECOVERY & RETRY")
    print("=" * 50)
    
    print("\n1. Retry Configuration:")
    print("-" * 30)
    client = Athena(max_retries=3, timeout=10)
    print(f"✅ Max retries: {client.http.max_retries}")
    print(f"✅ Timeout: {client.http.timeout} seconds")
    print(f"✅ Backoff factor: {client.http.backoff_factor}")
    
    print("\n2. Successful Recovery Example:")
    print("-" * 30)
    try:
        # This should work and demonstrate successful API calls
        results = client.search("aspirin", size=5)
        print(f"✅ Successfully found {len(results.all())} concepts")
        print(f"✅ First concept: {results.all()[0].name if results.all() else 'None'}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demo_error_types():
    """Demonstrate the different error types and their characteristics."""
    print("\n📋 ERROR TYPE HIERARCHY")
    print("=" * 50)
    
    print("\nError Types and Their Purposes:")
    print("-" * 40)
    
    error_types = [
        ("AthenaError", "Base class for all client exceptions"),
        ("NetworkError", "DNS, connection, socket issues"),
        ("TimeoutError", "Request timeout issues"),
        ("ClientError", "4xx HTTP status codes"),
        ("ServerError", "5xx HTTP status codes"),
        ("AuthenticationError", "401/403 authentication issues"),
        ("RateLimitError", "429 rate limiting issues"),
        ("ValidationError", "Data validation failures"),
        ("APIError", "API-specific error responses"),
    ]
    
    for error_type, description in error_types:
        print(f"✅ {error_type:<20} - {description}")


def demo_troubleshooting():
    """Demonstrate troubleshooting suggestions."""
    print("\n💡 TROUBLESHOOTING FEATURES")
    print("=" * 50)
    
    print("\n1. Error Messages Include:")
    print("-" * 30)
    print("✅ Clear explanation of what went wrong")
    print("✅ Context about where the error occurred")
    print("✅ Specific troubleshooting suggestions")
    print("✅ Error codes for programmatic handling")
    print("✅ User-friendly language (not technical jargon)")
    
    print("\n2. Example Troubleshooting Flow:")
    print("-" * 30)
    print("1. User encounters an error")
    print("2. Error message explains the problem")
    print("3. Troubleshooting section provides specific steps")
    print("4. User can take action to resolve the issue")
    print("5. If needed, error code allows for programmatic handling")


def demo_best_practices():
    """Demonstrate best practices for error handling."""
    print("\n🎯 ERROR HANDLING BEST PRACTICES")
    print("=" * 50)
    
    print("\n1. Always Use Try-Catch:")
    print("-" * 30)
    print("```python")
    print("try:")
    print("    results = athena.search('aspirin')")
    print("    print(f'Found {len(results.all())} concepts')")
    print("except NetworkError as e:")
    print("    print(f'Network issue: {e}')")
    print("except APIError as e:")
    print("    print(f'API issue: {e}')")
    print("except Exception as e:")
    print("    print(f'Unexpected error: {e}')")
    print("```")
    
    print("\n2. Check Error Types:")
    print("-" * 30)
    print("✅ NetworkError - Retry after network issues")
    print("✅ TimeoutError - Increase timeout or retry")
    print("✅ ClientError - Check request parameters")
    print("✅ ServerError - Wait and retry later")
    print("✅ AuthenticationError - Check credentials")
    print("✅ RateLimitError - Implement backoff strategy")
    
    print("\n3. Use Error Codes for Logic:")
    print("-" * 30)
    print("```python")
    print("try:")
    print("    concept = athena.details(concept_id)")
    print("except APIError as e:")
    print("    if e.error_code == 'CONCEPT_NOT_FOUND':")
    print("        # Handle missing concept")
    print("    elif e.error_code == 'INVALID_ID':")
    print("        # Handle invalid ID format")
    print("```")


def main():
    """Run the comprehensive error handling demo."""
    print("🚀 ATHENA CLIENT - ENHANCED ERROR HANDLING DEMO")
    print("=" * 60)
    print("This demo showcases how the athena-client provides clear,")
    print("actionable error messages for various failure scenarios.")
    print("=" * 60)
    
    demo_error_types()
    demo_network_errors()
    demo_api_errors()
    demo_http_errors()
    demo_error_recovery()
    demo_troubleshooting()
    demo_best_practices()
    
    print("\n" + "=" * 60)
    print("🎉 ERROR HANDLING DEMO COMPLETE")
    print("=" * 60)
    print("✅ All error scenarios demonstrated")
    print("✅ Clear, actionable error messages shown")
    print("✅ Troubleshooting suggestions provided")
    print("✅ Best practices outlined")
    print("\nThe athena-client now provides comprehensive error handling")
    print("that helps users understand and resolve issues quickly!")


if __name__ == "__main__":
    main() 