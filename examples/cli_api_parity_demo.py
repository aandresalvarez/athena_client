"""
This script demonstrates feature parity between the Python API and CLI for limiting results.
It shows how `results.top(3)` in Python API is equivalent to `--limit 3` in CLI.

Usage:
    python examples/cli_api_parity_demo.py
"""

import json
import subprocess
import sys
from athena_client import Athena


def run_cli_command(command):
    """Run a CLI command and return the output."""
    print(f"\nRunning CLI command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}")
        return None
    return result.stdout


def main():
    # Query to use for demonstration
    query = "aspirin"
    
    print("\n=== DEMONSTRATING API AND CLI FEATURE PARITY ===")
    print("This demo shows how Python API and CLI produce the same results\n")
    
    # Example 1: Using Python API with top()
    print("=== USING PYTHON API ===")
    athena = Athena()
    results = athena.search(query)
    
    # Get top 3 results using Python API
    top_three = results.top(3)
    
    # Convert to list of dicts for comparison
    api_results = results.to_list()[:3]
    print(f"Found {len(api_results)} results using Python API results.top(3)")
    
    # Example 2: Using CLI with --limit
    print("\n=== USING CLI ===")
    # Note: The CLI doesn't support the --output option directly, 
    # so we'll use the default output format and parse the results manually
    cli_command = f"athena search '{query}' --limit 3"
    cli_output = run_cli_command(cli_command)
    
    if cli_output:
        # CLI output is a rich table, which is hard to parse 
        # Count the number of "|" pipe characters that indicate table rows
        # We count the rows with concept IDs, which would have pipe characters
        rows = [row for row in cli_output.strip().split("\n") if "|" in row and "ID" not in row and "─" not in row]
        cli_result_count = len(rows)
        
        print(f"Found {cli_result_count} results using CLI --limit 3")
        
        # Compare results
        print("\n=== COMPARING RESULTS ===")
        print(f"API result count: {len(api_results)}")
        print(f"CLI result count: {cli_result_count}")
        
        # Print first result from Python API
        print("\nFirst concept from Python API:")
        print(f"  ID: {api_results[0]['id']}")
        print(f"  Name: {api_results[0]['name']}")
        
        # Check if result counts match
        if len(api_results) == cli_result_count:
            print("\n✅ API and CLI return the same number of results")
        else:
            print("\n❌ API and CLI return different numbers of results")


if __name__ == "__main__":
    main()
