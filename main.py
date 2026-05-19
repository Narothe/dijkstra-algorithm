import heapq


def format_cell(distance, previous_node):
    """Formatuje komórkę tabeli."""
    if distance == float('inf'):
        return "∞"
    if previous_node is None:
        return str(distance)
    return f"{distance}({previous_node})"


def print_dijkstra_table(step, visited, distances, previous, nodes, widths):
    """Wypisuje jeden wiersz tabeli z wyrównanymi kolumnami."""

    # Zbiór odwiedzonych wierzchołków
    L = "{" + ",".join(sorted(visited)) + "}"

    # Dane w wierszu
    row = [str(step), L]

    for node in nodes:
        row.append(format_cell(distances[node], previous[node]))

    # Wyrównanie każdej kolumny
    formatted = [
        value.ljust(widths[i])
        for i, value in enumerate(row)
    ]

    print(" | ".join(formatted))


def dijkstra(graph, start):
    # Wierzchołki oprócz startowego
    nodes = sorted([node for node in graph.keys() if node != start])

    # Inicjalizacja
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    previous = {node: None for node in graph}
    visited = set()

    priority_queue = [(0, start)]

    # ==========================
    # USTALENIE SZEROKOŚCI KOLUMN
    # ==========================
    headers = ["Nr etapu", "Zbiór L"] + nodes

    widths = []

    # Kolumna "Nr etapu"
    widths.append(max(len("Nr etapu"), 8))

    # Kolumna "Zbiór L"
    max_set_length = len("{" + ",".join(sorted(graph.keys())) + "}")
    widths.append(max(len("Zbiór L"), max_set_length))

    # Kolumny wierzchołków
    # Maksymalna możliwa wartość np. "999(A)"
    for node in nodes:
        widths.append(max(len(node), 8))

    # ==========================
    # NAGŁÓWEK
    # ==========================
    header_line = " | ".join(
        headers[i].ljust(widths[i])
        for i in range(len(headers))
    )

    print(header_line)
    print("-" * len(header_line))

    # Etap 0
    print_dijkstra_table(
        0, visited, distances, previous, nodes, widths
    )

    # ==========================
    # ALGORYTM DIJKSTRY
    # ==========================
    step = 1

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Pomijamy nieaktualne wpisy
        if current_distance > distances[current_node]:
            continue

        # Jeśli już odwiedzony
        if current_node in visited:
            continue

        # Dodanie do zbioru L
        visited.add(current_node)

        # Aktualizacja sąsiadów
        for neighbor, weight in graph[current_node].items():
            if neighbor in visited:
                continue

            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor)
                )

        # Wypisanie etapu
        print_dijkstra_table(
            step,
            visited,
            distances,
            previous,
            nodes,
            widths
        )

        step += 1

    return distances, previous


def get_path(previous, start, end):
    path = []
    current = end

    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()

    if path and path[0] == start:
        return path
    return None


def draw_graph(graph, shortest_path=None):
    """
    Rysuje skierowany graf z wagami.
    Najkrótsza ścieżka jest podświetlona na czerwono.
    """

    import networkx as nx
    import matplotlib.pyplot as plt

    # Tworzymy figurę na początku
    plt.figure(figsize=(12, 7))

    # Tworzenie grafu skierowanego
    G = nx.DiGraph()

    # Dodawanie krawędzi
    for source, neighbors in graph.items():
        for target, weight in neighbors.items():
            G.add_edge(source, target, weight=weight)

    # Ręcznie ustawione pozycje dla znanych wierzchołków
    pos = {
        'A': (0, 2),
        'B': (1, 4),
        'C': (1, 2),
        'D': (3, 4),
        'E': (4, 2),
        'F': (5, 4),
        'G': (6, 2),
        'H': (3, 0)
    }

    # Sprawdzenie, czy istnieją wierzchołki bez pozycji (np. I)
    missing_nodes = [node for node in G.nodes if node not in pos]

    if missing_nodes:
        # Generujemy automatyczny układ dla całego grafu
        auto_pos = nx.spring_layout(G, seed=42)

        # Uzupełniamy brakujące pozycje
        for node in missing_nodes:
            pos[node] = auto_pos[node]

    # Rozmiar wierzchołków
    node_size = 1200

    # Rysowanie wierzchołków
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_size,
        node_color='white',
        edgecolors='black',
        linewidths=2
    )

    # Etykiety wierzchołków
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=14,
        font_weight='bold'
    )

    # Wszystkie krawędzie
    nx.draw_networkx_edges(
        G,
        pos,
        edge_color='black',
        arrows=True,
        arrowsize=30,
        arrowstyle='-|>',
        width=2,
        connectionstyle='arc3,rad=0.08',
        min_source_margin=25,
        min_target_margin=25
    )

    # Etykiety wag
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=12,
        label_pos=0.55,
        bbox=dict(
            facecolor='white',
            edgecolor='none',
            alpha=0.8,
            pad=0.2
        )
    )

    # Podświetlenie najkrótszej ścieżki
    if shortest_path and len(shortest_path) > 1:
        path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=path_edges,
            edge_color='red',
            arrows=True,
            arrowsize=35,
            arrowstyle='-|>',
            width=4,
            connectionstyle='arc3,rad=0.08',
            min_source_margin=25,
            min_target_margin=25
        )

    plt.title("Graf skierowany (najkrótsza ścieżka zaznaczona na czerwono)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


# ==========================
# GRAF
# ==========================
graph = {
    'A': {'B': 6, 'C': 1, 'D': 3},
    'B': {'F': 4},
    'C': {'B': 7, 'E': 6, 'F': 12},
    'D': {'B': 2, 'G': 14, 'E': 3, 'H': 9},
    'E': {'F': 4},
    'F': {'H': 1, 'I': 5},
    'G': {'J': 2},
    'H': {'G': 3, 'J': 8, 'I': 2},
    'I': {'J': 4},
    'J': {}
}

# Wierzchołek startowy
start = 'A'

# Wierzchołek końcowy
end = 'J'

# Uruchomienie algorytmu
distances, previous = dijkstra(graph, start)

# Wyświetlenie wszystkich odległości
print(f"Najkrótsze odległości od wierzchołka {start}:")
for node in sorted(distances):
    print(f"{start} -> {node}: {distances[node]}")

# Odtworzenie ścieżki
path = get_path(previous, start, end)

print(f"\nNajkrótsza ścieżka z {start} do {end}:")
print(" -> ".join(path))
print(f"Koszt: {distances[end]}")

# Rysowanie grafu
draw_graph(graph, path)