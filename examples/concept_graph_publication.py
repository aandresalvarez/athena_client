#!/usr/bin/env python3
"""
Publication-quality Concept Relationship Graph (NetworkX + Matplotlib)

Quick start (pip users):
  pip install athena-client networkx matplotlib
  # Optional (better hierarchical layout):
  #   macOS: brew install graphviz
  #   python: pip install pygraphviz

Run:
  python examples/concept_graph_publication.py [concept_id] [depth] [zoom]
  # Example:
  python examples/concept_graph_publication.py 1127433 3 2

Notes:
- Saves SVG and PNG into the output/ directory (headless-friendly).
- If Graphviz/pygraphviz is available, uses 'dot' for a cleaner DAG layout;
  otherwise falls back to a Kamada–Kawai layout.
"""

from __future__ import annotations

import os
import sys
from textwrap import wrap
from typing import Dict, Tuple

# Ensure local package import when run from repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Headless-safe backend
try:
    import matplotlib  # type: ignore
except Exception:
    print("Missing dependency 'matplotlib'. Install with: pip install matplotlib")
    raise
matplotlib.use("Agg")

try:
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib import cm
except Exception:
    print("Matplotlib is installed, but pyplot failed to load.")
    raise

try:
    import networkx as nx  # type: ignore
except Exception:
    print("Missing dependency 'networkx'. Install with: pip install networkx")
    raise

from athena_client import Athena
from athena_client.models import ConceptRelationsGraph


def fetch_graph(concept_id: int, depth: int, zoom_level: int) -> ConceptRelationsGraph:
    athena = Athena()
    return athena.graph(concept_id=concept_id, depth=depth, zoom_level=zoom_level)


def build_graph(graph: ConceptRelationsGraph) -> Tuple[nx.DiGraph, Dict[int, str], Dict[int, int]]:
    G = nx.DiGraph()
    for link in graph.links:
        label = link.relationshipName or link.relationshipId or ""
        G.add_edge(link.source, link.target, label=label)

    labels = {t.id: t.name for t in graph.terms}
    depths = {t.id: t.depth for t in graph.terms}
    return G, labels, depths


def _scale(values, lo=400, hi=2000):
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        return [(lo + hi) // 2 for _ in values]
    return [lo + (v - vmin) * (hi - lo) / (vmax - vmin) for v in values]


def compute_layout(G: nx.DiGraph) -> Dict[int, Tuple[float, float]]:
    # Prefer Graphviz 'dot' layout if available
    try:
        from networkx.drawing.nx_agraph import graphviz_layout  # type: ignore

        return graphviz_layout(G, prog="dot")
    except Exception:
        # Fallback to a force-directed layout that doesn't require SciPy
        return nx.spring_layout(G, seed=42)


def draw(G: nx.DiGraph, labels: Dict[int, str], depths: Dict[int, int], out_base: str) -> None:
    # Determine max depth for color scaling
    max_depth = max(depths.values()) if depths else 1
    node_colors = [cm.viridis((depths.get(n, 0)) / max(1, max_depth)) for n in G.nodes()]

    # Size by degree if no weights available in the labels dict
    degrees = [G.degree(n) for n in G.nodes()]
    sizes = _scale(degrees, lo=500, hi=2200)

    # Layout
    pos = compute_layout(G)

    # Figure
    plt.figure(figsize=(10, 8), dpi=300)
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=sizes,
        node_color=node_colors,
        linewidths=0.8,
        edgecolors="#333",
    )
    nx.draw_networkx_edges(
        G,
        pos,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=12,
        width=1.2,
        alpha=0.85,
        connectionstyle="arc3,rad=0.08",
    )

    # Wrap labels for readability
    def wl(n: int) -> str:
        name = labels.get(n, str(n))
        text = "\n".join(wrap(name, width=18))
        return f"{text}\n({n})"

    nx.draw_networkx_labels(G, pos, labels={n: wl(n) for n in G.nodes()}, font_size=7)

    edge_labels = {(u, v): d.get("label", "") for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6, label_pos=0.5)

    plt.axis("off")
    plt.tight_layout()

    os.makedirs(os.path.dirname(out_base), exist_ok=True)
    svg_path = f"{out_base}.svg"
    png_path = f"{out_base}.png"
    plt.savefig(svg_path, bbox_inches="tight", facecolor="white")
    plt.savefig(png_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Saved: {svg_path}\nSaved: {png_path}")


def main(argv: list[str]) -> int:
    concept_id = int(argv[1]) if len(argv) > 1 else 1127433
    depth = int(argv[2]) if len(argv) > 2 else 3
    zoom = int(argv[3]) if len(argv) > 3 else 2

    graph = fetch_graph(concept_id, depth, zoom)
    G, labels, depths = build_graph(graph)

    out_base = os.path.join(
        "output", f"concept_graph_publication_{concept_id}_d{depth}_z{zoom}"
    )
    draw(G, labels, depths, out_base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
