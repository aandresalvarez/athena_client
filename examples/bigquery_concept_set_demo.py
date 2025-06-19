#!/usr/bin/env python3
"""
Example: Generating a Validated Concept Set with Google BigQuery

This script demonstrates how to use the athena-client to generate a concept
set by connecting to an OMOP CDM hosted in Google BigQuery.

Prerequisites:
1.  Install the necessary client libraries:
    pip install "athena-client[bigquery]"

2.  Authenticate with Google Cloud. The simplest way for local development
    is to use the gcloud CLI:
    gcloud auth application-default login

    This command will open a browser window for you to log in and will store
    your credentials locally where the client library can find them.

3.  Ensure your Google Cloud user or service account has permissions to read
    the BigQuery dataset containing your OMOP tables (e.g., "BigQuery Data Viewer").

Usage:
    python examples/bigquery_concept_set_demo.py
"""
import asyncio
import os
import sys
import logging

# Add parent directory to Python path for local execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from athena_client import Athena

# --- Configuration for Your BigQuery OMOP CDM ---
# Replace these with your actual Google Cloud Project ID and BigQuery dataset name.
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "som-rit-starr-training")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "starr_omop_cdm5_deid_1pcent_lite_20191024")
# -------------------------------------------------

def create_bigquery_connection_string() -> str:
    """
    Creates the SQLAlchemy connection string for Google BigQuery.
    """
    if GCP_PROJECT_ID == "your-gcp-project-id" or BIGQUERY_DATASET == "your_omop_dataset":
        print("⚠️  WARNING: Please update GCP_PROJECT_ID and BIGQUERY_DATASET variables in this script.")
        print("           You can also set them as environment variables.")
        sys.exit(1)

    # The format for a BigQuery connection string is "bigquery://<project_id>/<dataset>"
    return f"bigquery://{GCP_PROJECT_ID}/{BIGQUERY_DATASET}"


async def main():
    """
    Main function to connect to BigQuery and generate a concept set.
    """
    # Suppress noisy network error logs from BigQuery/Google libraries
    for noisy_logger in [
        "google.auth.transport.requests",
        "google.auth._default",
        "google.resumable_media",
        "google.api_core.retry",
        "urllib3.connectionpool",
        "requests.packages.urllib3.connectionpool",
        "sqlalchemy.engine.Engine",
        "pybigquery.sqlalchemy_bigquery",
        "sqlalchemy_bigquery",
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.ERROR)

    print("🚀 Athena Client with Google BigQuery Demo")
    print("=" * 50)

    # 1. Create the BigQuery connection string
    db_connection_string = create_bigquery_connection_string()
    print(f"Connecting to BigQuery dataset: {BIGQUERY_DATASET} in project {GCP_PROJECT_ID}")

    # 2. Initialize the Athena client
    athena = Athena()
    
    # 3. Define the search query
    search_query = "Diabetes Mellitus"
    print(f"\n🔍 Generating concept set for: '{search_query}'")

    try:
        # 4. Generate the concept set
        # The client uses the connection string to talk to your BigQuery OMOP instance.
        concept_set = await athena.generate_concept_set(
            query=search_query,
            db_connection_string=db_connection_string
        )

        # 5. Print the results
        print("\n" + "="*50)
        print("✅ Concept Set Generation Complete!")
        print("="*50)

        metadata = concept_set.get("metadata", {})
        if metadata.get("status") == "SUCCESS":
            print(f"Status: {metadata['status']} ✨")
            print(f"Strategy Used: {metadata['strategy_used']}")
            warnings = metadata.get('warnings', [])
            if warnings:
                print("\nWarnings:")
                for warning in warnings:
                    print(f"  - {warning}")
            print(f"\nFound {len(concept_set.get('concept_ids', []))} total concepts (including descendants).")
            seed_concepts = metadata.get('seed_concepts', [])
            if seed_concepts:
                print(f"The set was built from {len(seed_concepts)} validated standard concept(s):")
                for concept_id in seed_concepts:
                    print(f"  - Concept ID: {concept_id}")
        else:
            print(f"Status: {metadata.get('status', 'FAILURE')} ❌")
            # Always print the full reason, even if it's not the default
            print(f"Reason: {metadata.get('reason', 'An unknown error occurred.')}")
            suggestions = metadata.get('suggestions', [])
            if suggestions:
                print("\nSuggestions:")
                for suggestion in suggestions:
                    if suggestion:
                        print(f"  - {suggestion}")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred during the process: {e}")
        print("   Please check the following:")
        print("   - Have you authenticated with Google Cloud? (run 'gcloud auth application-default login')")
        print("   - Is your GCP_PROJECT_ID and BIGQUERY_DATASET correct?")
        print("   - Does your user account have permissions to read the BigQuery dataset?")

if __name__ == "__main__":
    # Ensure you have the required dependencies installed and supported Python version
    import sys
    if sys.version_info >= (3, 10):
        print("❌ BigQuery support requires Python 3.9 or lower due to upstream dependency limitations.")
        print("   Please use a Python 3.9 environment for BigQuery support.")
        sys.exit(1)
    try:
        import sqlalchemy_bigquery
    except ImportError:
        print("❌ Missing BigQuery dependencies.")
        print('   Please install them with: pip install "athena-client[bigquery]"')
        sys.exit(1)
    
    asyncio.run(main())
