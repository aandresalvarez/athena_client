#!/usr/bin/env python3
"""
Simple test to check URL building.
"""
from athena_client import Athena
from athena_client.settings import get_settings

# Check settings
settings = get_settings()
print(f"Base URL from settings: {settings.ATHENA_BASE_URL}")

# Create client
client = Athena()
print(f"Client HTTP base URL: {client.http.base_url}")

# Test URL building
test_url = client.http._build_url("/concepts")
print(f"Built URL for /concepts: {test_url}")

# Test with query parameters
test_url_with_params = client.http._build_url("/concepts?query=aspirin")
print(f"Built URL for /concepts?query=aspirin: {test_url_with_params}") 