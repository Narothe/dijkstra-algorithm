"""Longest path search.

Unlike shortest paths, the longest path problem is NP-hard on general graphs, so
two strategies are used:

* **DAG** (no cycle reachable from the start): dynamic programming over a
  topological order, O(V + E).
* **Graph with cycles** (and every undirected graph): exhaustive search over
  *simple* paths (no repeated vertex). Exponential in the worst case, so it is
  limited by `max_expansions`; fine for the small graphs this app is aimed at.

The result is the same `Result` object as for Dijkstra; vertices that cannot be
reached from the start keep the distance `INF` ("not reachable").
"""

from __future__ import annotations

import sys

from .core import INF, Graph, GraphError, Result, Step, validate

DEFAULT_LIMIT = 2_000_000


def reachable(graph: Graph, start: str) -> set[str]:
    seen, stack = {start}, [start]
    while stack:
        for nxt in graph[stack.pop()]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def topological_order(graph: Graph, nodes: set[str]) -> list[str] | None:
    """Kahn's algorithm on the subgraph induced by `nodes`; None if it has a cycle."""
    indegree = {n: 0 for n in nodes}
    for u in nodes:
        for v in graph[u]:
            if v in nodes:
                indegree[v] += 1
    queue = sorted(n for n, d in indegree.items() if d == 0)
    order = []
    while queue:
        u = queue.pop(0)
        order.append(u)
        for v in graph[u]:
            if v in nodes:
                indegree[v] -= 1
                if indegree[v] == 0:
                    queue.append(v)
    return order if len(order) == len(nodes) else None


def longest_path(graph: Graph, start: str, max_expansions: int = DEFAULT_LIMIT) -> Result:
    """Longest (maximum total weight) path from `start` to every vertex.

    Returns a `Result`; `result.method` is "dag" or "search".
    Raises GraphError if the search budget is exhausted on a cyclic graph.
    """
    validate(graph, allow_negative=True)
    if start not in graph:
        raise GraphError(f"Start vertex {start!r} is not in the graph.")

    nodes = reachable(graph, start)
    order = topological_order(graph, nodes)
    if order is not None:
        result = _longest_dag(graph, start, order)
        result.method = "dag"
    else:
        result = _longest_search(graph, start, max_expansions)
        result.method = "search"
    return result


def _longest_dag(graph: Graph, start: str, order: list[str]) -> Result:
    best: dict[str, float] = {n: INF for n in graph}       # INF = not reached
    previous: dict[str, str | None] = {n: None for n in graph}
    best[start] = 0
    visited: list[str] = []
    steps = [Step(0, None, [], dict(best), dict(previous))]

    for u in order:
        visited.append(u)
        for v, w in graph[u].items():
            if best[v] == INF or best[u] + w > best[v]:
                best[v] = best[u] + w
                previous[v] = u
        steps.append(Step(len(steps), u, list(visited), dict(best), dict(previous)))
    return Result(start, best, previous, steps)


def _longest_search(graph: Graph, start: str, max_expansions: int) -> Result:
    best: dict[str, float] = {n: INF for n in graph}
    previous: dict[str, str | None] = {n: None for n in graph}
    best[start] = 0
    # path[-1] is the current vertex; `parents` remembers the best path to each vertex
    best_paths: dict[str, list[str]] = {start: [start]}
    on_path = {start}
    path = [start]
    budget = [max_expansions]

    def visit(u: str, total: float) -> None:
        for v, w in graph[u].items():
            if v in on_path:
                continue
            budget[0] -= 1
            if budget[0] < 0:
                raise GraphError(
                    "The graph has cycles and is too large to search exhaustively "
                    "for the longest path (the problem is NP-hard). "
                    "Try a smaller graph or remove some cycles."
                )
            new_total = total + w
            path.append(v)
            on_path.add(v)
            if best[v] == INF or new_total > best[v]:
                best[v] = new_total
                best_paths[v] = list(path)
            visit(v, new_total)
            on_path.discard(v)
            path.pop()

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(graph) + 200))
    try:
        visit(start, 0)
    except RecursionError:
        raise GraphError("The graph is too deep to search for the longest path.") from None
    finally:
        sys.setrecursionlimit(old_limit)

    for node, p in best_paths.items():
        previous[node] = p[-2] if len(p) > 1 else None
    # `previous` of different vertices may come from different paths, so store
    # the full paths on the result for exact reconstruction.
    result = Result(start, best, previous, [])
    result.paths = best_paths
    visited = sorted(best_paths, key=lambda n: (len(best_paths[n]), n))
    result.steps = [
        Step(0, None, [], {n: (0 if n == start else INF) for n in graph}, {n: None for n in graph}),
        Step(1, None, visited, dict(best), dict(previous)),
    ]
    return result
