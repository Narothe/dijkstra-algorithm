"""Shortest path search: Dijkstra's algorithm (non-negative weights)."""

from __future__ import annotations

import heapq

from .core import INF, Graph, GraphError, Result, Step, validate


def shortest_path(graph: Graph, start: str) -> Result:
    """Shortest (minimum total weight) path from `start` to every vertex.

    Runs Dijkstra's algorithm and records every stage. Raises GraphError on
    negative weights or unknown vertices.
    """
    validate(graph)
    if start not in graph:
        raise GraphError(f"Start vertex {start!r} is not in the graph.")

    distances = {node: INF for node in graph}
    distances[start] = 0
    previous: dict[str, str | None] = {node: None for node in graph}
    visited: list[str] = []
    done: set[str] = set()

    def snapshot(current: str | None) -> Step:
        return Step(len(steps), current, list(visited), dict(distances), dict(previous))

    steps: list[Step] = []
    steps.append(snapshot(None))

    queue = [(0, start)]
    while queue:
        dist, node = heapq.heappop(queue)
        if node in done or dist > distances[node]:
            continue
        done.add(node)
        visited.append(node)
        for neighbour, weight in graph[node].items():
            if neighbour in done:
                continue
            candidate = dist + weight
            if candidate < distances[neighbour]:
                distances[neighbour] = candidate
                previous[neighbour] = node
                heapq.heappush(queue, (candidate, neighbour))
        steps.append(snapshot(node))

    return Result(start, distances, previous, steps)


dijkstra = shortest_path  # classic name, kept as an alias
