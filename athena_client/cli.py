"""
Command-line interface for the Athena client.

This module provides a CLI for interacting with the Athena API.
"""

import asyncio
import csv
import json
import sys
from io import StringIO
from typing import Any, List, Optional, cast

try:
    import click
except ImportError:
    click = None  # type: ignore

try:
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.syntax import Syntax
except ImportError:
    rich = None  # type: ignore
    Console = None  # type: ignore
    Table = None  # type: ignore
    Syntax = None  # type: ignore

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from athena_client.models import Concept

from . import Athena, __version__


def _create_client(
    base_url: Optional[str],
    token: Optional[str],
    timeout: Optional[int],
    retries: Optional[int],
) -> Athena:
    """
    Create an Athena client with the given parameters.

    Args:
        base_url: Base URL for the Athena API
        token: Bearer token for authentication
        timeout: HTTP timeout in seconds
        retries: Maximum number of retry attempts

    Returns:
        Athena client
    """
    return Athena(
        base_url=base_url,
        token=token,
        timeout=timeout,
        max_retries=retries,
    )


def _format_output(data: object, output: str, console: Any = None) -> None:
    """
    Format and print data based on the requested output format.

    Args:
        data: Data to format and print
        output: Output format (json, yaml, table, pretty, csv)
        console: Rich console for pretty printing
    """

    # Convert Pydantic models and SearchResult to dicts/lists for serialization
    def to_serializable(obj: Any) -> Any:
        # If the object has a .to_list() method (e.g., SearchResult), use it
        if hasattr(obj, "to_list") and callable(obj.to_list):
            return to_serializable(obj.to_list())
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif isinstance(obj, list):
            return [to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        return obj

    if output == "json":
        serializable = to_serializable(data)
        if isinstance(serializable, str):
            print(serializable)
        else:
            print(json.dumps(serializable, indent=2))
    elif output == "yaml":
        try:
            import yaml

            print(yaml.dump(to_serializable(data)))
        except (ImportError, ModuleNotFoundError):
            print(
                "The 'pyyaml' package is required for YAML output. "
                "Install with 'pip install \"athena-client[yaml]\"'"
            )
            sys.exit(1)
    elif output == "csv":
        try:
            import csv
            import io

            serializable = to_serializable(data)
            # Only accept list of dicts for CSV
            if (
                isinstance(serializable, list)
                and serializable
                and isinstance(serializable[0], dict)
            ):
                data_list = serializable
            elif isinstance(serializable, dict):
                data_list = [serializable]
            else:
                data_list = []

            if not data_list:
                print("No results found")
                return

            output_buffer = io.StringIO()
            # Collect all field names from all items to ensure no fields are dropped
            fieldnames = []
            seen_fields = set()
            for item in data_list:
                for key in item.keys():
                    if key not in seen_fields:
                        fieldnames.append(key)
                        seen_fields.add(key)

            writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
            writer.writeheader()
            for item in data_list:
                writer.writerow(item)

            print(output_buffer.getvalue())
        except ImportError:
            print("CSV output requires the csv module.")
            sys.exit(1)
    elif output == "table" and console is not None and rich is not None:
        # Try to convert any object with model_dump/model_dump_json to dict/list
        # for table rendering
        if hasattr(data, "to_list") and Table is not None:
            results = cast(Any, data).to_list()
        elif isinstance(data, list) and data and hasattr(data[0], "model_dump"):
            results = [cast(Any, item).model_dump() for item in data]
        elif isinstance(data, dict):
            results = [data]
        elif hasattr(data, "model_dump"):
            results = [cast(Any, data).model_dump()]
        else:
            results = [data]

        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        # Dynamically determine columns by collecting all keys from all results
        # This ensures optional fields are not missed if they're absent in the first row.
        columns = []
        seen_cols = set()
        for item in results:
            if isinstance(item, dict):
                for key in item.keys():
                    if key not in seen_cols:
                        columns.append(key)
                        seen_cols.add(key)
            elif not seen_cols:
                # Fallback for non-dict items
                if isinstance(item, list):
                    columns = [str(i) for i in range(len(item))]
                else:
                    columns = [str(item)]
                seen_cols.update(columns)

        if Table is not None:
            table = Table(title="Athena Results")
            for col in columns:
                table.add_column(str(col))
            for item in results:
                if isinstance(item, dict):
                    row = [str(item.get(col, "")) for col in columns]
                elif isinstance(item, list):
                    row = [str(x) for x in item]
                else:
                    row = [str(item)]
                table.add_row(*row)
            console.print(table)
            return
    elif output == "pretty" and console is not None and rich is not None:
        # Use rich's pretty printing
        console.print(data)
    else:
        serializable = to_serializable(data)
        if isinstance(serializable, str):
            print(serializable)
        else:
            print(json.dumps(serializable, indent=2))


if click:
    @click.group()
    @click.version_option(__version__)
    @click.option(
        "--base-url",
        envvar="ATHENA_BASE_URL",
        help="Base URL for the Athena API",
    )
    @click.option(
        "--token",
        envvar="ATHENA_TOKEN",
        help="Bearer token for authentication",
    )
    @click.option(
        "--timeout",
        type=int,
        envvar="ATHENA_TIMEOUT_SECONDS",
        help="HTTP timeout in seconds",
    )
    @click.option(
        "--retries",
        type=int,
        envvar="ATHENA_MAX_RETRIES",
        help="Maximum number of retry attempts",
    )
    @click.option(
        "--output",
        "-o",
        type=click.Choice(["json", "yaml", "table", "pretty", "csv"]),
        default="table",
        help="Output format",
    )
    @click.pass_context
    def cli(
        ctx: Any,
        base_url: Optional[str],
        token: Optional[str],
        timeout: Optional[int],
        retries: Optional[int],
        output: str,
    ) -> None:
        """Athena Client CLI - Interact with the OHDSI Athena API."""
        ctx.ensure_object(dict)
        ctx.obj["base_url"] = base_url
        ctx.obj["token"] = token
        ctx.obj["timeout"] = timeout
        ctx.obj["retries"] = retries
        ctx.obj["output"] = output

        # Set up rich console if available
        if rich is not None:
            ctx.obj["console"] = cast(Any, Console)()
        else:
            ctx.obj["console"] = None

    @cli.command()
    @click.argument("query")
    @click.option("--fuzzy/--no-fuzzy", default=False, help="Enable fuzzy matching")
    @click.option("--page-size", type=int, default=20, help="Number of results per page")
    @click.option("--page", type=int, default=0, help="Page number (0-indexed)")
    @click.option(
        "--limit",
        type=int,
        help="Limit the number of results (equivalent to .top() in Python API)",
    )
    @click.option("--domain", help="Filter by domain")
    @click.option("--vocabulary", help="Filter by vocabulary")
    @click.option(
        "--output",
        "-o",
        type=click.Choice(["json", "yaml", "table", "pretty", "csv"]),
        default=None,
        help="Output format (overrides global setting)",
    )
    @click.pass_context
    def search(
        ctx: Any,
        query: str,
        fuzzy: bool,
        page_size: int,
        page: int,
        limit: Optional[int],
        domain: Optional[str],
        vocabulary: Optional[str],
        output: Optional[str],
    ) -> None:
        """Search for concepts in the Athena vocabulary."""
        click.echo(
            "[Responsible Usage] Please avoid excessive or automated requests. "
            "Abuse may result in your IP being blocked by the Athena API provider. "
            "Use filters and limits where possible.",
            err=True,
        )

        client = _create_client(
            ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
        )

        # If limit is set and less than page_size, use limit for page_size.
        # This minimizes data transfer.
        effective_page_size = page_size
        if limit is not None and (page_size is None or limit < page_size):
            effective_page_size = limit

        results = client.search(
            query,
            fuzzy=fuzzy,
            page_size=effective_page_size,
            page=page,
            domain=domain,
            vocabulary=vocabulary,
        )

        # Apply limit if specified (in case server returns more than requested).
        # This is also for future-proofing.
        limited_results: Optional[List[Concept]] = None
        if limit is not None:
            limited_results = results.top(limit)

        # Get the appropriate output based on the format
        output_data: Any
        if limited_results is not None:
            output_data = limited_results
        else:
            output_data = results

        # Determine output format: command-line option overrides global
        output_format = output or ctx.obj.get("output", "table")
        _format_output(output_data, output_format, ctx.obj.get("console"))

    @cli.command(name="generate-set")
    @click.argument("query")
    @click.option(
        "--db-connection",
        required=True,
        envvar="OMOP_DB_CONNECTION",
        help="SQLAlchemy connection string for the OMOP database.",
    )
    @click.option(
        "--strategy",
        type=click.Choice(["fallback", "strict"]),
        default="fallback",
        help="Generation strategy.",
    )
    @click.option(
        "--no-descendants",
        is_flag=True,
        help="Do not include descendant concepts in the set.",
    )
    @click.pass_context
    def generate_set(
        ctx: Any,
        query: str,
        db_connection: str,
        strategy: str,
        no_descendants: bool,
    ) -> None:
        """Generate a validated concept set for a given query."""

        client = _create_client(
            ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
        )

        click.echo(f"Generating concept set for '{query}'...", err=True)

        try:
            concept_set = client.generate_concept_set(
                query=query,
                db_connection_string=db_connection,
                strategy=strategy,
                include_descendants=not no_descendants,
            )

            _format_output(concept_set, ctx.obj["output"], ctx.obj.get("console"))

            metadata = concept_set.get("metadata", {})
            if metadata.get("status") == "SUCCESS":
                click.secho(
                    f"\nSuccess! Found {len(concept_set.get('concept_ids', []))} concepts.",
                    fg="green",
                    err=True,
                )
                click.secho(
                    f"Strategy used: {metadata.get('strategy_used')}",
                    err=True,
                )
                for warning in metadata.get("warnings", []):
                    click.secho(
                        f"Warning: {warning}",
                        fg="yellow",
                        err=True,
                    )
            else:
                click.secho(
                    f"\nFailure: {metadata.get('reason')}",
                    fg="red",
                    err=True,
                )
        except Exception as e:  # pragma: no cover - defensive
            click.secho(
                f"An unexpected error occurred: {e}",
                fg="red",
                err=True,
            )
            sys.exit(1)

    @cli.command()
    @click.argument("concept_id", type=int)
    @click.pass_context
    def details(ctx: Any, concept_id: int) -> None:
        """Get detailed information for a specific concept."""
        client = _create_client(
            ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
        )

        result = client.details(concept_id)
        _format_output(result, ctx.obj["output"], ctx.obj.get("console"))

    @cli.command()
    @click.argument("concept_id", type=int)
    @click.option("--relationship-id", help="Filter by relationship type")
    @click.option(
        "--only-standard/--all", default=False, help="Only include standard concepts"
    )
    @click.pass_context
    def relationships(
        ctx: Any,
        concept_id: int,
        relationship_id: Optional[str],
        only_standard: bool,
    ) -> None:
        """Get relationships for a specific concept."""
        client = _create_client(
            ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
        )

        result = client.relationships(concept_id)
        _format_output(result, ctx.obj["output"], ctx.obj.get("console"))

    @cli.command()
    @click.argument("concept_id", type=int)
    @click.option("--depth", type=int, default=10, help="Maximum depth of relationships")
    @click.option("--zoom-level", type=int, default=4, help="Zoom level for the graph")
    @click.pass_context
    def graph(ctx: Any, concept_id: int, depth: int, zoom_level: int) -> None:
        """Get relationship graph for a specific concept."""
        client = _create_client(
            ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
        )

        result = client.graph(
            concept_id,
            depth=depth,
            zoom_level=zoom_level,
        )
        _format_output(result, ctx.obj["output"], ctx.obj.get("console"))

    @cli.command()
    @click.argument("concept_id", type=int)
    @click.pass_context
    def summary(ctx: Any, concept_id: int) -> None:
        """Get a comprehensive summary for a concept."""
        client = _create_client(
            ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
        )

        result = client.summary(concept_id)
        _format_output(result, ctx.obj["output"], ctx.obj.get("console"))

else:
    # Fallback if click is not installed
    def cli(*args: Any, **kwargs: Any) -> None:
        """Fallback for when click is not installed."""
        print(
            "The 'click' package is required for the CLI. "
            "Install with: pip install 'athena-client[cli]'",
            file=sys.stderr
        )
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    if click:
        cli(obj={})  # pylint: disable=unexpected-keyword-arg
    else:
        cli()


if __name__ == "__main__":
    main()
