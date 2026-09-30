"""Tests for the SHORTEST path search (Dijkstra) in dijkstra_app/shortest.py."""

import unittest

from dijkstra_app.core import INF, GraphError, format_table
from dijkstra_app.shortest import shortest_path

G = {
    "A": {"B": 6, "C": 1, "D": 3},
    "B": {"F": 4},
    "C": {"B": 7, "E": 6, "F": 12},
    "D": {"B": 2, "G": 14, "E": 3, "H": 9},
    "E": {"F": 4},
    "F": {"H": 1, "I": 5},
    "G": {"J": 2},
    "H": {"G": 3, "J": 8, "I": 2},
    "I": {"J": 4},
    "J": {},
}


class ShortestPathTests(unittest.TestCase):
    def test_shortest_distances_and_path(self):
        r = shortest_path(G, "A")
        self.assertEqual(r.method, "dijkstra")
        self.assertEqual(r.distances["J"], 15)
        self.assertEqual(r.path_to("J"), ["A", "D", "B", "F", "H", "G", "J"])

    def test_shortest_unreachable_vertex(self):
        r = shortest_path({"A": {}, "B": {}}, "A")
        self.assertEqual(r.distances["B"], INF)
        self.assertIsNone(r.path_to("B"))

    def test_shortest_rejects_negative_weight(self):
        with self.assertRaises(GraphError):
            shortest_path({"A": {"B": -1}, "B": {}}, "A")

    def test_shortest_rejects_unknown_vertices(self):
        with self.assertRaises(GraphError):
            shortest_path(G, "Z")
        with self.assertRaises(GraphError):
            shortest_path({"A": {"B": 1}}, "A")

    def test_shortest_records_every_step(self):
        r = shortest_path(G, "A")
        self.assertEqual(len(r.steps), len(G) + 1)
        self.assertEqual(r.steps[0].visited, [])
        self.assertIn("Set L", format_table(r, G))


if __name__ == "__main__":
    unittest.main()
