"""
This script demonstrates feature parity between the Python API and CLI for limiting results.
It shows how `results.top(3)` in Python API is equivalent to `--limit 3` in CLI.

Usage:
    python examples/cli_api_parity_test.py
"""

import json
import subprocess
import sys
from athena_client import Athena

def run_cli_command(command):
    """Run a CLI command and return the output."""
    print(f"Running CLI command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {result.stderr}")
        return None
    return result.stdout

def main():
    print("\n=== TESTING CLI AND API FEATURE PARITY FOR RESULT LIMITING ===")
    
    query = "aspirin"
    limit = 3
    
    # Use the Python API
    print(f"\nUsing Python API with top({limit}):")
    athena = Athena()
    api_results = athena.search(query)
    top_results = api_results.top(limit)
    
    print(f"- API returned {len(top_results)} results")
    if len(top_results) > 0:
        print(f"- First result ID: {top_results[0].id}")
        print(f"- First result name: {top_results[0].name}")
    
    # Get all concept IDs from the API results
    api_concept_ids = [concept.id for concept in top_results]
    print(f"- API concept IDs: {api_concept_ids}")
    
    # Use the CLI with the --limit option
    print(f"\nUsing CLI with --limit {limit}:")
    cli_output = run_cli_command(f"athena -o json search '{query}' --limit {limit}")
    
    if cli_output:
        try:
            cli_results = json.loads(cli_output)
            print(f"- CLI returned {len(cli_results)} results")
            
            if len(cli_results) > 0:
                print(f"- First result ID: {cli_results[0].get('id')}")
                print(f"- First result name: {cli_results[0].get('name')}")
            
            # Get all concept IDs from the CLI results
            cli_concept_ids = [result.get('id') for result in cli_results]
            print(f"- CLI concept IDs: {cli_concept_ids}")
            
            # Compare the results
            if api_concept_ids == cli_concept_ids:
                print("\n✅ PASSED: API and CLI return the same concept IDs")
            else:
                print("\n❌ FAILED: API and CLI return different concept IDs")
                
            if len(top_results) == len(cli_results):
                print("✅ PASSED: API and CLI return the same number of results")
            else:
                print("❌ FAILED: API and CLI return different numbers of results")
        
        except json.JSONDecodeError:
            print("- Failed to parse CLI output as JSON")
            print("\nCLI output preview:")
            print("--------------------")
            print(cli_output[:500] + "..." if len(cli_output) > 500 else cli_output)
            print("--------------------")
    
if __name__ == "__main__":
    main()
