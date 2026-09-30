"""Reading and writing graphs: edge-list text and JSON."""

from __future__ import annotations

import json
from pathlib import Path

from .core import Graph, GraphError


def parse_edges(text: str, directed: bool = True) -> Graph:
    """Parse lines like ``A B 6`` (also ``A->B:6`` or ``A,B,6``) into a graph.

    A line with a single name (``K``) adds an isolated vertex.
    Lines starting with ``#`` and blank lines are ignored.
    """
    graph: Graph = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        for sep in ("->", "=>", ",", ":", ";"):
            line = line.replace(sep, " ")
        parts = line.split()
        if len(parts) == 1:
            graph.setdefault(parts[0], {})
            continue
        if len(parts) != 3:
            raise GraphError(f"Line {number}: expected 'FROM TO WEIGHT', got {raw.strip()!r}.")
        source, target, weight_text = parts
        try:
            weight = float(weight_text)
        except ValueError:
            raise GraphError(f"Line {number}: {weight_text!r} is not a number.") from None
        if weight < 0:
            raise GraphError(f"Line {number}: negative weights are not supported.")
        weight = int(weight) if weight.is_integer() else weight
        graph.setdefault(source, {})[target] = weight
        graph.setdefault(target, {})
        if not directed:
            graph[target][source] = weight
    return graph


def graph_to_edges(graph: Graph, directed: bool = True) -> str:
    """Inverse of :func:`parse_edges`."""
    lines, seen = [], set()
    for source in sorted(graph):
        for target, weight in graph[source].items():
            if not directed and (target, source) in seen:
                continue
            seen.add((source, target))
            lines.append(f"{source} {target} {weight}")
        if not graph[source] and not any(source in e for e in graph.values()):
            lines.append(source)
    return "\n".join(lines)


def load_json(path: str | Path) -> tuple[Graph, bool]:
    """Load ``{"directed": true, "graph": {"A": {"B": 1}}}`` (or a bare graph dict)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "graph" in data and isinstance(data["graph"], dict):
        return data["graph"], bool(data.get("directed", True))
    return data, True


def save_json(path: str | Path, graph: Graph, directed: bool = True) -> None:
    payload = {"directed": directed, "graph": graph}
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
