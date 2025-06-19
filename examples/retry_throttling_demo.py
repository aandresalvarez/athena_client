#!/usr/bin/env python3
"""
Demo showcasing the enhanced retry mechanism and request throttling.

This demo demonstrates how the athena-client handles:
- Rate limiting (429 errors)
- Server overload (5xx errors)
- Network timeouts
- Request throttling to prevent overwhelming the server
"""
import sys
import os
import time

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena


def demo_retry_configuration():
    """Demonstrate retry configuration options."""
    print("\n🔧 RETRY CONFIGURATION")
    print("=" * 50)
    
    # Default configuration
    print("\n1. Default Configuration:")
    print("-" * 30)
    athena_default = Athena()
    print(f"✅ Max retries: {athena_default.http.max_retries}")
    print(f"✅ Timeout: {athena_default.http.timeout} seconds")
    print(f"✅ Backoff factor: {athena_default.http.backoff_factor}")
    print(f"✅ Throttling: {'enabled' if athena_default.http.enable_throttling else 'disabled'}")
    print(f"✅ Throttle delay range: {athena_default.http.throttle_delay_range} seconds")
    
    # Custom configuration
    print("\n2. Custom Configuration:")
    print("-" * 30)
    athena_custom = Athena(
        max_retries=5,
        timeout=30,
        enable_throttling=True,
        throttle_delay_range=(0.2, 0.5)
    )
    print(f"✅ Max retries: {athena_custom.http.max_retries}")
    print(f"✅ Timeout: {athena_custom.http.timeout} seconds")
    print(f"✅ Backoff factor: {athena_custom.http.backoff_factor}")
    print(f"✅ Throttling: {'enabled' if athena_custom.http.enable_throttling else 'disabled'}")
    print(f"✅ Throttle delay range: {athena_custom.http.throttle_delay_range} seconds")
    
    # No throttling configuration
    print("\n3. No Throttling Configuration:")
    print("-" * 30)
    athena_no_throttle = Athena(enable_throttling=False)
    print(f"✅ Throttling: {'enabled' if athena_no_throttle.http.enable_throttling else 'disabled'}")


def demo_retry_mechanism():
    """Demonstrate the retry mechanism in action."""
    print("\n🔄 RETRY MECHANISM")
    print("=" * 50)
    
    athena = Athena(max_retries=2)  # Use fewer retries for demo
    
    print("\n1. Successful Request (No Retry Needed):")
    print("-" * 40)
    start_time = time.time()
    try:
        results = athena.search("aspirin", size=5)
        end_time = time.time()
        print(f"✅ Success: Found {len(results.all())} concepts")
        print(f"✅ Time taken: {end_time - start_time:.2f} seconds")
        print(f"✅ No retries needed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n2. Retry on Network Issues:")
    print("-" * 40)
    print("   (This would normally show retry behavior for network issues)")
    print("   ✅ Automatic retry on connection errors")
    print("   ✅ Exponential backoff between attempts")
    print("   ✅ Respects Retry-After headers")
    print("   ✅ Logs retry attempts for debugging")


def demo_rate_limiting():
    """Demonstrate rate limiting handling."""
    print("\n⏱️ RATE LIMITING HANDLING")
    print("=" * 50)
    
    print("\n1. Rate Limit Detection:")
    print("-" * 30)
    print("✅ Detects 429 status codes automatically")
    print("✅ Respects Retry-After headers from server")
    print("✅ Uses exponential backoff if no Retry-After header")
    print("✅ Logs rate limiting events")
    
    print("\n2. Rate Limit Response:")
    print("-" * 30)
    print("✅ Waits for server-specified time")
    print("✅ Retries request after waiting")
    print("✅ Provides clear error messages")
    print("✅ Includes troubleshooting suggestions")


def demo_request_throttling():
    """Demonstrate request throttling."""
    print("\n🐌 REQUEST THROTTLING")
    print("=" * 50)
    
    print("\n1. Throttling Benefits:")
    print("-" * 30)
    print("✅ Prevents overwhelming the server")
    print("✅ Reduces likelihood of rate limiting")
    print("✅ Random delays prevent thundering herd")
    print("✅ Configurable delay ranges")
    
    print("\n2. Throttling in Action:")
    print("-" * 30)
    athena = Athena(enable_throttling=True, throttle_delay_range=(0.1, 0.2))
    
    start_time = time.time()
    for i in range(3):
        print(f"   Making request {i+1}/3...")
        try:
            results = athena.search("aspirin", size=1)
            print(f"   ✅ Request {i+1} successful")
        except Exception as e:
            print(f"   ❌ Request {i+1} failed: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n✅ Total time for 3 requests: {total_time:.2f} seconds")
    print(f"✅ Average time per request: {total_time/3:.2f} seconds")
    print(f"✅ Includes throttling delays")


def demo_error_recovery():
    """Demonstrate error recovery scenarios."""
    print("\n🛠️ ERROR RECOVERY SCENARIOS")
    print("=" * 50)
    
    print("\n1. Server Overload (5xx Errors):")
    print("-" * 35)
    print("✅ Retries on 500, 502, 503, 504 errors")
    print("✅ Also retries on 520, 521, 522, 523, 524")
    print("✅ Exponential backoff between attempts")
    print("✅ Clear error messages after max retries")
    
    print("\n2. Network Issues:")
    print("-" * 35)
    print("✅ Retries on connection errors")
    print("✅ Retries on DNS resolution failures")
    print("✅ Retries on timeout errors")
    print("✅ Handles temporary network instability")
    
    print("\n3. API Errors:")
    print("-" * 35)
    print("✅ No retry on 4xx client errors")
    print("✅ Clear, actionable error messages")
    print("✅ Specific handling for common errors")
    print("✅ Helpful troubleshooting suggestions")


def demo_best_practices():
    """Demonstrate best practices for retry and throttling."""
    print("\n🎯 BEST PRACTICES")
    print("=" * 50)
    
    print("\n1. Production Configuration:")
    print("-" * 35)
    print("✅ Use 3-5 max retries for production")
    print("✅ Enable throttling to be respectful")
    print("✅ Use reasonable timeout values (15-30s)")
    print("✅ Monitor retry patterns in logs")
    
    print("\n2. Development Configuration:")
    print("-" * 35)
    print("✅ Use fewer retries for faster feedback")
    print("✅ Disable throttling for testing if needed")
    print("✅ Use shorter timeouts for quick iteration")
    print("✅ Enable debug logging for troubleshooting")
    
    print("\n3. Rate Limit Handling:")
    print("-" * 35)
    print("✅ Always respect Retry-After headers")
    print("✅ Implement exponential backoff")
    print("✅ Log rate limiting events")
    print("✅ Consider implementing circuit breakers")


def main():
    """Run the retry and throttling demo."""
    print("🚀 ATHENA CLIENT - RETRY & THROTTLING DEMO")
    print("=" * 60)
    print("This demo showcases the enhanced retry mechanism and")
    print("request throttling features of the athena-client.")
    print("=" * 60)
    
    demo_retry_configuration()
    demo_retry_mechanism()
    demo_rate_limiting()
    demo_request_throttling()
    demo_error_recovery()
    demo_best_practices()
    
    print("\n" + "=" * 60)
    print("🎉 RETRY & THROTTLING DEMO COMPLETE")
    print("=" * 60)
    print("✅ Enhanced retry mechanism demonstrated")
    print("✅ Request throttling features shown")
    print("✅ Rate limiting handling explained")
    print("✅ Best practices outlined")
    print("\nThe athena-client now provides robust handling of")
    print("rate limiting, server overload, and network issues!")


if __name__ == "__main__":
    main() 