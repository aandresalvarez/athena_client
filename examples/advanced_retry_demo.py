#!/usr/bin/env python3
"""
Advanced retry configuration and detailed error reporting demo.

This demo showcases:
- Fine-grained retry control
- Detailed retry error reporting
- Developer configuration options
- Request throttling control
"""
import sys
import os
import time

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena
from athena_client.exceptions import RetryFailedError, NetworkError, APIError


def demo_retry_configuration():
    """Demonstrate advanced retry configuration options."""
    print("\n🔧 ADVANCED RETRY CONFIGURATION")
    print("=" * 50)
    
    print("\n1. Client-Level Configuration:")
    print("-" * 35)
    athena = Athena(
        max_retries=5,
        retry_delay=1.0,
        enable_throttling=True,
        throttle_delay_range=(0.2, 0.5),
        timeout=30
    )
    print(f"✅ Max retries: {athena.max_retries}")
    print(f"✅ Retry delay: {athena.retry_delay} seconds")
    print(f"✅ Throttling: {'enabled' if athena.enable_throttling else 'disabled'}")
    print(f"✅ Throttle range: {athena.throttle_delay_range} seconds")
    print(f"✅ Timeout: {athena.http.timeout} seconds")
    
    print("\n2. Call-Level Override:")
    print("-" * 35)
    try:
        # Override retry settings for this specific call
        results = athena.search(
            "aspirin",
            max_retries=2,      # Override max retries
            retry_delay=0.5     # Override retry delay
        )
        print(f"✅ Search successful with custom retry settings")
    except Exception as e:
        print(f"❌ Search failed: {e}")


def demo_detailed_error_reporting():
    """Demonstrate detailed retry error reporting."""
    print("\n📊 DETAILED ERROR REPORTING")
    print("=" * 50)
    
    print("\n1. Normal Error (No Retry):")
    print("-" * 30)
    athena = Athena(max_retries=0)  # No retries
    try:
        results = athena.search("aspirin")
        print("✅ Search successful")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")
        print(f"   Message: {e}")
    
    print("\n2. Retry Error with Details:")
    print("-" * 30)
    # This would normally show retry behavior, but we'll simulate it
    print("   (In a real scenario with network issues, you would see:)")
    print("   ✅ RetryFailedError with detailed information:")
    print("   ✅ Maximum attempts made")
    print("   ✅ Last error details")
    print("   ✅ Complete retry history")
    print("   ✅ Specific troubleshooting suggestions")


def demo_retry_control_scenarios():
    """Demonstrate different retry control scenarios."""
    print("\n🎛️ RETRY CONTROL SCENARIOS")
    print("=" * 50)
    
    print("\n1. Aggressive Retry (High Volume):")
    print("-" * 35)
    athena_aggressive = Athena(
        max_retries=10,
        retry_delay=0.1,
        enable_throttling=False
    )
    print(f"✅ Max retries: {athena_aggressive.max_retries}")
    print(f"✅ Retry delay: {athena_aggressive.retry_delay} seconds")
    print(f"✅ Throttling: {'enabled' if athena_aggressive.enable_throttling else 'disabled'}")
    print("   Use case: High-volume processing where speed is critical")
    
    print("\n2. Conservative Retry (Production):")
    print("-" * 35)
    athena_conservative = Athena(
        max_retries=3,
        retry_delay=2.0,
        enable_throttling=True,
        throttle_delay_range=(0.3, 0.8)
    )
    print(f"✅ Max retries: {athena_conservative.max_retries}")
    print(f"✅ Retry delay: {athena_conservative.retry_delay} seconds")
    print(f"✅ Throttling: {'enabled' if athena_conservative.enable_throttling else 'disabled'}")
    print("   Use case: Production systems where reliability is critical")
    
    print("\n3. Development Retry (Fast Feedback):")
    print("-" * 35)
    athena_dev = Athena(
        max_retries=1,
        retry_delay=0.5,
        enable_throttling=False
    )
    print(f"✅ Max retries: {athena_dev.max_retries}")
    print(f"✅ Retry delay: {athena_dev.retry_delay} seconds")
    print(f"✅ Throttling: {'enabled' if athena_dev.enable_throttling else 'disabled'}")
    print("   Use case: Development where fast feedback is important")


def demo_error_analysis():
    """Demonstrate how to analyze retry errors."""
    print("\n🔍 ERROR ANALYSIS")
    print("=" * 50)
    
    print("\n1. RetryFailedError Analysis:")
    print("-" * 30)
    print("```python")
    print("try:")
    print("    results = athena.search('aspirin')")
    print("except RetryFailedError as e:")
    print("    print(f'Max attempts: {e.max_attempts}')")
    print("    print(f'Attempts made: {len(e.retry_history) + 1}')")
    print("    print(f'Last error: {e.last_error}')")
    print("    print(f'Retry history: {e.retry_history}')")
    print("    # Error message includes all this information automatically")
    print("```")
    
    print("\n2. Error Type Analysis:")
    print("-" * 30)
    print("```python")
    print("try:")
    print("    results = athena.search('aspirin')")
    print("except RetryFailedError as e:")
    print("    if isinstance(e.last_error, NetworkError):")
    print("        print('Network connectivity issue')")
    print("    elif isinstance(e.last_error, TimeoutError):")
    print("        print('Server response timeout')")
    print("    elif isinstance(e.last_error, APIError):")
    print("        print('API-specific error')")
    print("```")


def demo_best_practices():
    """Demonstrate best practices for retry configuration."""
    print("\n🎯 BEST PRACTICES")
    print("=" * 50)
    
    print("\n1. Production Configuration:")
    print("-" * 30)
    print("✅ Use 3-5 max retries for production")
    print("✅ Enable throttling to be respectful to the server")
    print("✅ Use reasonable retry delays (1-3 seconds)")
    print("✅ Monitor retry patterns and adjust accordingly")
    print("✅ Log retry failures for analysis")
    
    print("\n2. Development Configuration:")
    print("-" * 30)
    print("✅ Use 1-2 max retries for faster feedback")
    print("✅ Disable throttling for testing if needed")
    print("✅ Use shorter retry delays (0.5-1 second)")
    print("✅ Enable debug logging for troubleshooting")
    
    print("\n3. Error Handling:")
    print("-" * 30)
    print("✅ Always catch RetryFailedError for retry failures")
    print("✅ Analyze retry history to understand failure patterns")
    print("✅ Implement circuit breakers for persistent failures")
    print("✅ Provide user-friendly error messages")


def main():
    """Run the advanced retry demo."""
    print("🚀 ATHENA CLIENT - ADVANCED RETRY DEMO")
    print("=" * 60)
    print("This demo showcases advanced retry configuration and")
    print("detailed error reporting features.")
    print("=" * 60)
    
    demo_retry_configuration()
    demo_detailed_error_reporting()
    demo_retry_control_scenarios()
    demo_error_analysis()
    demo_best_practices()
    
    print("\n" + "=" * 60)
    print("🎉 ADVANCED RETRY DEMO COMPLETE")
    print("=" * 60)
    print("✅ Advanced retry configuration demonstrated")
    print("✅ Detailed error reporting features shown")
    print("✅ Retry control scenarios explained")
    print("✅ Best practices outlined")
    print("\nThe athena-client now provides enterprise-grade retry")
    print("control with detailed error reporting!")


if __name__ == "__main__":
    main() 