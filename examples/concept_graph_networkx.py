#!/usr/bin/env python3
"""
Draw a concept relationship graph using NetworkX.

Quick start (pip users):
  pip install athena-client networkx matplotlib
  python examples/concept_graph_networkx.py 1127433 3 2

From repo with Hatch:
  make install
  hatch run pip install networkx matplotlib
  hatch run python examples/concept_graph_networkx.py 1127433 3 2

Auth (if needed by your server):
  export ATHENA_CLIENT_ID="your-client-id"
  export ATHENA_PRIVATE_KEY="your-private-key"

Notes:
- Saves a PNG to the output/ directory (headless friendly).
- Falls back to a tiny in-memory graph if API access fails, so drawing code
  can still be validated.
"""

import os
import sys
from typing import Optional

# Ensure local package import when run from repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import matplotlib  # type: ignore
except Exception as e:  # pragma: no cover - guidance for users
    print("Missing dependency 'matplotlib'. Install with: pip install matplotlib")
    raise

# Use a non-interactive backend for headless environments
matplotlib.use("Agg")
try:
    import matplotlib.pyplot as plt  # type: ignore
except Exception as e:  # pragma: no cover
    print("Matplotlib is installed, but pyplot failed to load. Ensure GUI backends are not required.")
    raise

try:
    import networkx as nx  # type: ignore
except Exception as e:  # pragma: no cover
    print("Missing dependency 'networkx'. Install with: pip install networkx")
    raise

from athena_client import Athena
from athena_client.models import ConceptRelationsGraph, GraphLink, GraphTerm


def fetch_graph(concept_id: int, depth: int, zoom_level: int) -> ConceptRelationsGraph:
    """Fetch graph from Athena API or provide a minimal fallback if it fails."""
    athena = Athena()
    try:
        return athena.graph(concept_id=concept_id, depth=depth, zoom_level=zoom_level)
    except Exception as e:
        print(f"[warn] Failed to fetch API graph: {e}\n       Falling back to sample graph for drawing validation.")
        # Minimal fallback graph with two nodes and one link
        terms = [
            GraphTerm(id=concept_id, name=f"Concept {concept_id}", weight=1, depth=0, count=1, isCurrent=True),
            GraphTerm(id=concept_id + 1, name=f"Related {concept_id+1}", weight=1, depth=1, count=1, isCurrent=False),
        ]
        links = [GraphLink(source=concept_id, target=concept_id + 1, relationshipId="Related to", relationshipName="Related to")]
        return ConceptRelationsGraph(terms=terms, links=links, connectionsCount=1)


def build_nx_graph(graph: ConceptRelationsGraph) -> tuple[nx.DiGraph, dict[int, str]]:
    """Build a NetworkX DiGraph and node label map from ConceptRelationsGraph."""
    G = nx.DiGraph()
    for link in graph.links:
        label = link.relationshipName or link.relationshipId or ""
        G.add_edge(link.source, link.target, label=label)

    # Node labels: prefer names; include ID for clarity
    node_labels = {t.id: f"{t.name}\n({t.id})" for t in graph.terms}
    return G, node_labels


def draw_and_save(G: nx.DiGraph, node_labels: dict[int, str], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, labels=node_labels, with_labels=True, node_size=800, node_color="lightblue", font_size=8)
    edge_labels = {(u, v): d.get("label", "") for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
    plt.title("Concept Relationship Graph")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main(argv: list[str]) -> int:
    concept_id: int = int(argv[1]) if len(argv) > 1 else 1127433
    depth: int = int(argv[2]) if len(argv) > 2 else 3
    zoom_level: int = int(argv[3]) if len(argv) > 3 else 2

    graph = fetch_graph(concept_id, depth, zoom_level)
    print(f"Fetched graph: terms={len(graph.terms)}, links={len(graph.links)}")
    G, labels = build_nx_graph(graph)

    out_path = f"output/concept_graph_{concept_id}_d{depth}_z{zoom_level}.png"
    draw_and_save(G, labels, out_path)
    print(f"Saved graph visualization to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
