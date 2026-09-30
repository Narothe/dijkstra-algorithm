"""Command-line interface."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .longest import longest_path
from .core import GraphError, format_number, format_table, INF
from .shortest import shortest_path
from .graph_io import load_json, parse_edges

DEMO = """\
A B 6
A C 1
A D 3
B F 4
C B 7
C E 6
C F 12
D B 2
D G 14
D E 3
D H 9
E F 4
F H 1
F I 5
G J 2
H G 3
H J 8
H I 2
I J 4
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dijkstra",
        description="Shortest paths with Dijkstra's algorithm. "
                    "Run without arguments to open the graphical app.",
    )
    p.add_argument("graph", nargs="?", help="graph file (.json or edge-list .txt)")
    p.add_argument("-s", "--start", help="start vertex")
    p.add_argument("-e", "--end", help="end vertex (prints the path to it)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--shortest", action="store_true",
                      help="find the SHORTEST path with Dijkstra (default)")
    mode.add_argument("--longest", action="store_true",
                      help="find the LONGEST path (exact; exponential on cyclic graphs)")
    p.add_argument("--undirected", action="store_true", help="treat edges as two-way")
    p.add_argument("--demo", action="store_true", help="use the built-in example graph")
    p.add_argument("--table", action="store_true", help="print the step-by-step table")
    p.add_argument("--plot", action="store_true", help="show the graph in a window")
    p.add_argument("--save", metavar="FILE.png", help="save the drawing as an image")
    p.add_argument("--gui", action="store_true", help="open the graphical app")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # so "∞" prints on any Windows console
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    if args.gui or (not args.graph and not args.demo):
        from .gui import run
        run(args.graph)
        return 0

    try:
        if args.demo:
            graph, directed = parse_edges(DEMO), True
            graph.setdefault("J", {})
        elif args.graph.lower().endswith(".json"):
            graph, directed = load_json(args.graph)
        else:
            with open(args.graph, encoding="utf-8") as f:
                text = f.read()
            directed = not args.undirected
            graph = parse_edges(text, directed)
        if args.undirected and args.graph and args.graph.lower().endswith(".json"):
            directed = False
            for u, edges in list(graph.items()):
                for v, w in edges.items():
                    graph.setdefault(v, {}).setdefault(u, w)

        start = args.start or sorted(graph)[0]
        result = (longest_path if args.longest else shortest_path)(graph, start)
        path = result.path_to(args.end) if args.end else None
    except (GraphError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.table:
        print(format_table(result, graph), end="\n\n")

    kind = "Longest" if args.longest else "Shortest"
    print(f"{kind} distances from {start}:")
    for node in sorted(result.distances):
        d = result.distances[node]
        print(f"  {start} -> {node}: {'unreachable' if d == INF else format_number(d)}")

    if args.end:
        print()
        if path is None:
            print(f"No path from {start} to {args.end}.")
        else:
            print(f"{kind} path {start} -> {args.end}: {' -> '.join(path)}")
            print(f"Cost: {format_number(result.distances[args.end])}")

    if args.plot or args.save:
        import matplotlib
        if not args.plot:
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from .visualize import compute_layout, draw_graph
        fig, ax = plt.subplots(figsize=(11, 7))
        draw_graph(ax, graph, directed, pos=compute_layout(graph, start, directed), path=path, distances=result.distances,
                   title=f"{kind} paths from {start}")
        fig.tight_layout()
        if args.save:
            fig.savefig(args.save, dpi=150)
            print(f"\nImage saved to {args.save}")
        if args.plot:
            plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
