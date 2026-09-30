"""Tests for the LONGEST path search in dijkstra_app/longest.py."""

import unittest

from dijkstra_app.core import INF, GraphError
from dijkstra_app.graph_io import parse_edges
from dijkstra_app.longest import longest_path

LONGEST_DAG = {
    "A": {"B": 3, "C": 2},
    "B": {"D": 4, "C": 1},
    "C": {"D": 7},
    "D": {},
    "X": {},
}


class LongestPathTests(unittest.TestCase):
    def test_longest_on_dag(self):
        r = longest_path(LONGEST_DAG, "A")
        self.assertEqual(r.method, "dag")
        self.assertEqual(r.distances["D"], 11)          # A-B-C-D = 3+1+7
        self.assertEqual(r.path_to("D"), ["A", "B", "C", "D"])
        self.assertEqual(r.distances["X"], INF)
        self.assertIsNone(r.path_to("X"))

    def test_longest_on_cyclic_graph_uses_simple_paths(self):
        g = {"A": {"B": 1}, "B": {"C": 1, "A": 5}, "C": {"A": 9, "D": 1}, "D": {}}
        r = longest_path(g, "A")
        self.assertEqual(r.method, "search")
        self.assertEqual(r.path_to("D"), ["A", "B", "C", "D"])
        self.assertEqual(r.distances["D"], 3)
        self.assertEqual(r.distances["A"], 0)            # never a positive cycle back to start

    def test_longest_on_undirected_graph(self):
        g = parse_edges("A B 1\nB C 1\nA C 5\nC D 2", directed=False)
        r = longest_path(g, "A")
        self.assertEqual(r.path_to("D"), ["A", "C", "D"])   # 5+2 beats 1+1+2
        self.assertEqual(r.distances["D"], 7)
        self.assertEqual(r.path_to("B"), ["A", "C", "B"])   # 5+1 beats direct 1

    def test_longest_search_limit_raises(self):
        n = 12
        g = {str(i): {str(j): 1 for j in range(n) if j != i} for i in range(n)}
        with self.assertRaises(GraphError):
            longest_path(g, "0", max_expansions=1000)

    def test_longest_rejects_unknown_start(self):
        with self.assertRaises(GraphError):
            longest_path(LONGEST_DAG, "Z")

    def test_longest_records_steps(self):
        self.assertGreaterEqual(len(longest_path(LONGEST_DAG, "A").steps), 2)


if __name__ == "__main__":
    unittest.main()
