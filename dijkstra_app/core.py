"""Shared building blocks: graph type, Result/Step, validation, table formatting.

The algorithms live in `shortest.py` (Dijkstra) and `longest.py`."""

from __future__ import annotations

from dataclasses import dataclass, field

INF = float("inf")

Graph = dict[str, dict[str, float]]


class GraphError(ValueError):
    """Raised when a graph or query is invalid."""


@dataclass
class Step:
    """State of the algorithm after one stage."""

    number: int
    current: str | None            # vertex finalised in this stage (None for stage 0)
    visited: list[str]             # the set L, in the order vertices were finalised
    distances: dict[str, float]
    previous: dict[str, str | None]


@dataclass
class Result:
    start: str
    distances: dict[str, float]
    previous: dict[str, str | None]
    steps: list[Step] = field(default_factory=list)
    method: str = "dijkstra"
    paths: dict[str, list[str]] | None = None   # exact paths, when `previous` is not enough

    def path_to(self, end: str) -> list[str] | None:
        """Best path from start to `end`, or None if unreachable."""
        if end not in self.distances:
            raise GraphError(f"Unknown vertex: {end!r}")
        if self.distances[end] == INF:
            return None
        if self.paths is not None:
            return list(self.paths[end])
        path = []
        node: str | None = end
        while node is not None:
            path.append(node)
            node = self.previous[node]
        return path[::-1]


def validate(graph: Graph, allow_negative: bool = False) -> None:
    """Make sure every edge points to a known vertex and (by default) no weight is negative."""
    for source, edges in graph.items():
        for target, weight in edges.items():
            if target not in graph:
                raise GraphError(f"Edge {source} -> {target} points to an unknown vertex.")
            if weight < 0 and not allow_negative:
                raise GraphError(
                    f"Edge {source} -> {target} has negative weight {weight}; "
                    "Dijkstra's algorithm requires non-negative weights."
                )


def format_number(value: float) -> str:
    if value == INF:
        return "∞"
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def format_cell(distance: float, previous: str | None) -> str:
    if distance == INF:
        return "∞"
    if previous is None:
        return format_number(distance)
    return f"{format_number(distance)}({previous})"


def steps_to_rows(result: Result, graph: Graph) -> tuple[list[str], list[list[str]]]:
    """Return (header, rows) of the step-by-step table, ready for any UI."""
    nodes = sorted(n for n in graph if n != result.start)
    header = ["Step", "Set L"] + nodes
    rows = []
    for step in result.steps:
        row = [str(step.number), "{" + ",".join(sorted(step.visited)) + "}"]
        row += [format_cell(step.distances[n], step.previous[n]) for n in nodes]
        rows.append(row)
    return header, rows


def format_table(result: Result, graph: Graph) -> str:
    """Aligned plain-text version of the step table."""
    header, rows = steps_to_rows(result, graph)
    widths = [max(len(r[i]) for r in [header] + rows) for i in range(len(header))]
    line = lambda r: " | ".join(c.ljust(w) for c, w in zip(r, widths))
    out = [line(header), "-" * len(line(header))]
    out += [line(r) for r in rows]
    return "\n".join(out)
