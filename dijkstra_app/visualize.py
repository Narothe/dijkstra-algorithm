"""Graph drawing with networkx + matplotlib. Draws on any matplotlib Axes."""

from __future__ import annotations

from .core import Graph, format_number


def compute_layout(graph: Graph, start: str | None = None, directed: bool = True,
                   seed: int = 42) -> dict:
    """Positions for every vertex.

    Directed graphs with a known start are laid out in columns by hop count from
    the start (reads left to right like the algorithm). Otherwise kamada-kawai.
    """
    import networkx as nx

    G = nx.DiGraph()
    G.add_nodes_from(graph)
    for source, edges in graph.items():
        for target in edges:
            G.add_edge(source, target)
    if len(G) <= 2:
        return nx.circular_layout(G)
    if directed and start in G:
        levels = nx.single_source_shortest_path_length(G, start)
        last = max(levels.values()) + 1
        for node in G.nodes:
            G.nodes[node]["layer"] = levels.get(node, last)
        return nx.multipartite_layout(G, subset_key="layer", align="vertical")
    try:
        return nx.kamada_kawai_layout(G.to_undirected())
    except Exception:  # scipy missing or degenerate graph
        return nx.spring_layout(G, seed=seed)


def draw_graph(
    ax,
    graph: Graph,
    directed: bool = True,
    pos: dict | None = None,
    path: list[str] | None = None,
    visited: list[str] | None = None,
    current: str | None = None,
    distances: dict | None = None,
    title: str | None = None,
) -> dict:
    """Draw `graph` on `ax` and return the layout used.

    path      – vertices of the shortest path (edges drawn in red)
    visited   – finalised vertices (light green)
    current   – vertex finalised in the shown step (orange)
    distances – if given, shown under each vertex label
    """
    import networkx as nx

    G = nx.DiGraph()
    G.add_nodes_from(graph)
    for source, edges in graph.items():
        for target, weight in edges.items():
            G.add_edge(source, target, weight=weight)

    pos = pos or compute_layout(graph, directed=directed)
    visited = visited or []

    ax.clear()
    colours = []
    for node in G.nodes:
        if node == current:
            colours.append("#ffb347")
        elif node in visited:
            colours.append("#b6e3a8")
        else:
            colours.append("white")

    curved = list(G.edges) if directed else []
    straight = [] if directed else list(G.edges)
    longest = max((len(str(n)) for n in G.nodes), default=1)
    node_size = 900 + 330 * max(longest - 1, 0)
    margin = 12 + node_size ** 0.5 / 2.2
    kw = dict(arrows=directed, width=1.8)
    if directed:
        kw.update(arrowstyle="-|>", arrowsize=22, min_source_margin=margin, min_target_margin=margin)

    if straight:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=straight, edge_color="#444", **kw)
    if curved:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=curved, edge_color="#444",
                               connectionstyle="arc3,rad=0.12", **kw)

    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))
        red = {**kw, "width": 3.5}
        for edges in ([e for e in path_edges if e in curved],
                      [e for e in path_edges if e not in curved]):
            if edges:
                extra = {"connectionstyle": "arc3,rad=0.12"} if edges[0] in curved else {}
                nx.draw_networkx_edges(G, pos, ax=ax, edgelist=edges, edge_color="red",
                                       **red, **extra)

    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_size, node_color=colours,
                           edgecolors="black", linewidths=2)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=13, font_weight="bold")

    labels = {}
    for u, v, data in G.edges(data=True):
        if not directed and (v, u) in labels:
            continue
        labels[(u, v)] = format_number(data["weight"])
    nx.draw_networkx_edge_labels(
        G, pos, ax=ax, edge_labels=labels, font_size=11, label_pos=0.5, rotate=False,
        connectionstyle="arc3,rad=0.12" if directed else "arc3,rad=0",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=0.2),
    )

    if distances:
        for node, (x, y) in pos.items():
            text = format_number(distances[node])
            ax.annotate(f"d={text}", (x, y), xytext=(0, -(node_size ** 0.5) / 2 - 8), textcoords="offset points",
                        ha="center", fontsize=9, color="#0b5394")

    if title:
        ax.set_title(title)
    ax.set_axis_off()
    ax.margins(0.12)
    return pos
