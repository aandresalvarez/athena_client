"""
This script demonstrates feature parity between the Python API and CLI for limiting results.
It shows how `results.top(3)` in Python API is equivalent to `--limit 3` in CLI.

Usage:
    python examples/test_cli_api_parity.py
"""

import os
import sys
import json
from pathlib import Path

from click.testing import CliRunner
from athena_client import Athena
from athena_client.cli import cli

def test_search_limit_parity():
    """Test that CLI limit and API top() return the same results."""
    print("\n=== TESTING CLI AND API FEATURE PARITY FOR RESULT LIMITING ===")
    
    # Query to use for testing
    query = "aspirin"
    limit = 3
    
    # Use the API directly
    print(f"\nUsing Python API with top({limit}):")
    athena = Athena()
    api_results = athena.search(query)
    top_results = api_results.top(limit)
    print(f"- API returned {len(top_results)} results")
    print(f"- First result ID: {top_results[0].id}")
    print(f"- First result name: {top_results[0].name}")
    
    # Use the CLI directly via the Click testing runner
    print(f"\nUsing CLI with --limit {limit}:")
    runner = CliRunner()
    # Set up the environment to use the CLI
    # Use JSON output for easier parsing
    result = runner.invoke(cli, ["-o", "json", "search", query, "--limit", str(limit)])
    
    print(f"- CLI exit code: {result.exit_code}")
    # Check if the result is as expected
    if result.exit_code == 0:
        print("\nCLI command executed successfully")
        
        # Parse JSON output
        try:
            cli_results = json.loads(result.output)
            print(f"- CLI returned {len(cli_results)} results")
            
            if len(cli_results) > 0:
                print(f"- First result ID: {cli_results[0].get('id')}")
                print(f"- First result name: {cli_results[0].get('name')}")
                
                # Compare API and CLI results
                api_ids = [concept.id for concept in top_results]
                cli_ids = [result.get('id') for result in cli_results]
                
                print("\nComparing API and CLI results:")
                print(f"- API IDs: {api_ids}")
                print(f"- CLI IDs: {cli_ids}")
                
                if api_ids == cli_ids:
                    print("\n✅ PASS: API and CLI return the same concept IDs")
                else:
                    print("\n❌ FAIL: API and CLI return different concept IDs")
            
        except json.JSONDecodeError:
            print("- Failed to parse CLI output as JSON")
            print(f"\nCLI output preview:")
            print("--------------------")
            print(result.output[:500] + "..." if len(result.output) > 500 else result.output)
            print("--------------------")

if __name__ == "__main__":
    test_search_limit_parity()
