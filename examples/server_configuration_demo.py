#!/usr/bin/env python3
"""
Demo showcasing how to configure the athena-client to connect to different Athena servers.

This demo demonstrates:
- Connecting to the default public OHDSI Athena API
- Connecting to custom Athena servers
- Using environment variables for configuration
- Authentication with different servers
- Configuration for different network environments
"""
import sys
import os

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena


def demo_default_server():
    """Demonstrate connecting to the default public Athena server."""
    print("\n🌐 DEFAULT SERVER CONFIGURATION")
    print("=" * 50)
    
    print("\n1. Default Public OHDSI Athena API:")
    print("-" * 40)
    athena = Athena()
    print(f"✅ Base URL: {athena.http.base_url}")
    print(f"✅ Timeout: {athena.http.timeout} seconds")
    print(f"✅ Max retries: {athena.http.max_retries}")
    print(f"✅ Throttling: {'enabled' if athena.http.enable_throttling else 'disabled'}")
    
    # Test a simple search
    try:
        results = athena.search("aspirin", size=1)
        print(f"✅ Test search successful: Found {len(results.all())} concepts")
    except Exception as e:
        print(f"❌ Test search failed: {e}")


def demo_custom_server():
    """Demonstrate connecting to a custom Athena server."""
    print("\n🔧 CUSTOM SERVER CONFIGURATION")
    print("=" * 50)
    
    print("\n1. Custom Server with Direct Configuration:")
    print("-" * 40)
    
    # Example with a hypothetical custom server
    custom_athena = Athena(
        base_url="https://your-athena-server.com/api/v1",
        timeout=60,
        max_retries=5
    )
    print(f"✅ Base URL: {custom_athena.http.base_url}")
    print(f"✅ Timeout: {custom_athena.http.timeout} seconds")
    print(f"✅ Max retries: {custom_athena.http.max_retries}")
    
    print("\n2. Local Development Server:")
    print("-" * 40)
    local_athena = Athena(
        base_url="http://localhost:8080/api/v1",
        enable_throttling=False,  # Disable throttling for local dev
        timeout=30
    )
    print(f"✅ Base URL: {local_athena.http.base_url}")
    print(f"✅ Throttling: {'enabled' if local_athena.http.enable_throttling else 'disabled'}")
    print(f"✅ Timeout: {local_athena.http.timeout} seconds")


def demo_authentication():
    """Demonstrate authentication with different servers."""
    print("\n🔐 AUTHENTICATION CONFIGURATION")
    print("=" * 50)
    
    print("\n1. HMAC Authentication:")
    print("-" * 40)
    hmac_athena = Athena(
        base_url="https://your-hmac-athena.com/api/v1",
        client_id="your-client-id",
        private_key="your-private-key"
    )
    print(f"✅ Base URL: {hmac_athena.http.base_url}")
    print(f"✅ Authentication: HMAC configured")
    
    print("\n2. No Authentication (Public Server):")
    print("-" * 40)
    public_athena = Athena()  # Default public server
    print(f"✅ Base URL: {public_athena.http.base_url}")
    print(f"✅ Authentication: None (public access)")


def demo_environment_variables():
    """Demonstrate using environment variables for configuration."""
    print("\n🌍 ENVIRONMENT VARIABLE CONFIGURATION")
    print("=" * 50)
    
    print("\n1. Environment Variable Examples:")
    print("-" * 40)
    print("export ATHENA_BASE_URL='https://your-athena-server.com/api/v1'")
    print("export ATHENA_CLIENT_ID='your-client-id'")
    print("export ATHENA_PRIVATE_KEY='your-private-key'")
    print("export ATHENA_TIMEOUT_SECONDS='60'")
    print("export ATHENA_MAX_RETRIES='5'")
    
    print("\n2. .env File Example:")
    print("-" * 40)
    print("ATHENA_BASE_URL=https://your-athena-server.com/api/v1")
    print("ATHENA_CLIENT_ID=your-client-id")
    print("ATHENA_PRIVATE_KEY=your-private-key")
    print("ATHENA_TIMEOUT_SECONDS=60")
    print("ATHENA_MAX_RETRIES=5")
    
    print("\n3. Configuration Precedence:")
    print("-" * 40)
    print("1. Direct parameters in Athena() constructor")
    print("2. Environment variables (ATHENA_*)")
    print("3. Default values (public OHDSI Athena API)")


def demo_network_optimization():
    """Demonstrate configuration for different network environments."""
    print("\n⚡ NETWORK OPTIMIZATION")
    print("=" * 50)
    
    print("\n1. High-Latency Network (e.g., international):")
    print("-" * 40)
    high_latency_athena = Athena(
        base_url="https://remote-athena-server.com/api/v1",
        timeout=120,        # 2 minute timeout
        max_retries=5,      # More retries
        enable_throttling=True
    )
    print(f"✅ Timeout: {high_latency_athena.http.timeout} seconds")
    print(f"✅ Max retries: {high_latency_athena.http.max_retries}")
    print(f"✅ Throttling: {'enabled' if high_latency_athena.http.enable_throttling else 'disabled'}")
    
    print("\n2. Local Network (fast connection):")
    print("-" * 40)
    local_network_athena = Athena(
        base_url="https://local-athena-server.com/api/v1",
        timeout=30,         # 30 second timeout
        max_retries=3,      # Standard retries
        enable_throttling=True
    )
    print(f"✅ Timeout: {local_network_athena.http.timeout} seconds")
    print(f"✅ Max retries: {local_network_athena.http.max_retries}")
    
    print("\n3. Development Environment:")
    print("-" * 40)
    dev_athena = Athena(
        base_url="http://localhost:8080/api/v1",
        timeout=10,         # Short timeout for quick feedback
        max_retries=1,      # Minimal retries
        enable_throttling=False  # No throttling for dev
    )
    print(f"✅ Timeout: {dev_athena.http.timeout} seconds")
    print(f"✅ Max retries: {dev_athena.http.max_retries}")
    print(f"✅ Throttling: {'enabled' if dev_athena.http.enable_throttling else 'disabled'}")


def demo_cli_configuration():
    """Demonstrate CLI server configuration."""
    print("\n🖥️  CLI SERVER CONFIGURATION")
    print("=" * 50)
    
    print("\n1. Command-Line Options:")
    print("-" * 40)
    print("athena --base-url 'https://your-server.com/api/v1' search 'aspirin'")
    print("athena --base-url 'https://your-server.com/api/v1' details 1127433")
    print("athena --base-url 'https://your-server.com/api/v1' graph 1127433")
    
    print("\n2. Environment Variables for CLI:")
    print("-" * 40)
    print("export ATHENA_BASE_URL='https://your-server.com/api/v1'")
    print("athena search 'aspirin'  # Uses environment variables")
    
    print("\n3. CLI with Custom Timeout and Retries:")
    print("-" * 40)
    print("athena search 'aspirin' --timeout 60 --retries 5")


def demo_common_scenarios():
    """Demonstrate common server configuration scenarios."""
    print("\n📋 COMMON SERVER SCENARIOS")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Public OHDSI Athena",
            "config": "Athena()",
            "description": "Default public server, no authentication needed"
        },
        {
            "name": "Private Athena Instance",
            "config": "Athena(base_url='https://your-server.com/api/v1')",
            "description": "Custom server, may require authentication"
        },
        {
            "name": "Local Development",
            "config": "Athena(base_url='http://localhost:8080/api/v1')",
            "description": "Local server, disabled throttling"
        },
        {
            "name": "Authenticated Server",
            "config": "Athena(base_url='...', client_id='...', private_key='...')",
            "description": "Server requiring HMAC authentication"
        },
        {
            "name": "High-Latency Network",
            "config": "Athena(base_url='...', timeout=120, max_retries=5)",
            "description": "Remote server with extended timeouts"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   Config: {scenario['config']}")
        print(f"   Use case: {scenario['description']}")


def main():
    """Run the comprehensive server configuration demo."""
    print("🚀 ATHENA CLIENT - SERVER CONFIGURATION DEMO")
    print("=" * 60)
    print("This demo showcases how to configure the athena-client")
    print("to connect to different Athena API servers.")
    print("=" * 60)
    
    demo_default_server()
    demo_custom_server()
    demo_authentication()
    demo_environment_variables()
    demo_network_optimization()
    demo_cli_configuration()
    demo_common_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ Server configuration demo completed!")
    print("💡 Check the README.md for detailed configuration options.")
    print("🔧 Try modifying the examples above with your own server URLs.")


if __name__ == "__main__":
    main() 
