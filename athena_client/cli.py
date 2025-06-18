"""
Command-line interface for the Athena client.

This module provides a CLI for interacting with the Athena API.
"""
import json
import sys
from typing import Optional

try:
    import click
except ImportError:
    click = None  # type: ignore
    print(
        "The 'click' package is required for the CLI. "
        "Install with 'pip install \"athena-client[cli]\"'"
    )
    sys.exit(1)

try:
    import rich
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table
except ImportError:
    rich = None  # type: ignore
    Console = None  # type: ignore
    Syntax = None  # type: ignore
    Table = None  # type: ignore

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


def _format_output(
    data: object,
    output: str,
    console: Optional[Console] = None
) -> None:
    """
    Format and print data based on the requested output format.
    
    Args:
        data: Data to format and print
        output: Output format (json, yaml, table, pretty)
        console: Rich console for pretty printing
    """
    if output == "json":
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))
    elif output == "yaml":
        try:
            import yaml
        except ImportError:
            print(
                "The 'pyyaml' package is required for YAML output. "
                "Install with 'pip install \"athena-client[yaml]\"'"
            )
            sys.exit(1)
            
        print(yaml.dump(data))
    elif output == "table" and console is not None and rich is not None:
        if hasattr(data, "to_list"):
            # Handle SearchResult
            results = data.to_list()
            if not results:
                console.print("[yellow]No results found[/yellow]")
                return
                
            table = Table(title="Athena Concepts")
            
            # Add columns
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Code", style="magenta")
            table.add_column("Vocabulary", style="blue")
            table.add_column("Domain", style="yellow")
            table.add_column("Class", style="red")
            
            # Add rows
            for item in results:
                table.add_row(
                    str(item["id"]),
                    item["name"],
                    item["concept_code"],
                    item["vocabulary"]["name"],
                    item["domain"]["name"],
                    item["concept_class"]["name"],
                )
                
            console.print(table)
        else:
            # Just pretty-print JSON for other data types
            syntax = Syntax(
                json.dumps(data, indent=2, default=str),
                "json",
                theme="monokai",
                word_wrap=True,
            )
            console.print(syntax)
    elif output == "pretty" and console is not None and rich is not None:
        # Use rich's pretty printing
        console.print(data)
    else:
        # Fall back to regular JSON
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))


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
    "--output", "-o",
    type=click.Choice(["json", "yaml", "table", "pretty"]),
    default="table",
    help="Output format",
)
@click.pass_context
def cli(
    ctx: click.Context,
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
        ctx.obj["console"] = Console()
    else:
        ctx.obj["console"] = None


@cli.command()
@click.argument("query")
@click.option("--fuzzy/--no-fuzzy", default=False, help="Enable fuzzy matching")
@click.option("--page-size", type=int, default=20, help="Number of results per page")
@click.option("--page", type=int, default=0, help="Page number (0-indexed)")
@click.option("--domain", help="Filter by domain")
@click.option("--vocabulary", help="Filter by vocabulary")
@click.pass_context
def search(
    ctx: click.Context,
    query: str,
    fuzzy: bool,
    page_size: int,
    page: int,
    domain: Optional[str],
    vocabulary: Optional[str],
) -> None:
    """Search for concepts in the Athena vocabulary."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    results = client.search(
        query,
        fuzzy=fuzzy,
        page_size=page_size,
        page=page,
        domain=domain,
        vocabulary=vocabulary,
    )
    
    # Get the appropriate output based on the format
    if ctx.obj["output"] == "json":
        output_data = results.to_json()
    elif ctx.obj["output"] == "yaml":
        output_data = results.to_yaml()
    else:
        output_data = results
        
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.pass_context
def details(ctx: click.Context, concept_id: int) -> None:
    """Get detailed information for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.details(concept_id)
    
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.option("--relationship-id", help="Filter by relationship type")
@click.option(
    "--only-standard/--all",
    default=False,
    help="Only include standard concepts"
)
@click.pass_context
def relationships(
    ctx: click.Context,
    concept_id: int,
    relationship_id: Optional[str],
    only_standard: bool
) -> None:
    """Get relationships for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.relationships(
        concept_id,
        relationship_id=relationship_id,
        only_standard=only_standard,
    )
    
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.option("--depth", type=int, default=10, help="Maximum depth of relationships")
@click.option("--zoom-level", type=int, default=4, help="Zoom level for the graph")
@click.pass_context
def graph(
    ctx: click.Context, concept_id: int, depth: int, zoom_level: int
) -> None:
    """Get relationship graph for a specific concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.graph(
        concept_id,
        depth=depth,
        zoom_level=zoom_level,
    )
    
    if ctx.obj["output"] == "json":
        output_data = result.model_dump_json(indent=2)
    elif ctx.obj["output"] == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    else:
        output_data = result.model_dump()
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command()
@click.argument("concept_id", type=int)
@click.pass_context
def summary(ctx: click.Context, concept_id: int) -> None:
    """Get a comprehensive summary for a concept."""
    client = _create_client(
        ctx.obj["base_url"], ctx.obj["token"], ctx.obj["timeout"], ctx.obj["retries"]
    )
    
    result = client.summary(concept_id)
    
    # Convert Pydantic models to dicts for serialization
    output_data = {
        "details": result["details"].model_dump(),
        "relationships": result["relationships"].model_dump(),
        "graph": result["graph"].model_dump(),
    }
    
    _format_output(output_data, ctx.obj["output"], ctx.obj.get("console"))


@cli.command(name="caps")
@click.pass_context
def capabilities(ctx: click.Context) -> None:
    """List capabilities of the Athena client."""
    caps = Athena.capabilities()
    _format_output(caps, ctx.obj["output"], ctx.obj.get("console"))


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})  # pylint: disable=unexpected-keyword-arg


if __name__ == "__main__":
    main()
