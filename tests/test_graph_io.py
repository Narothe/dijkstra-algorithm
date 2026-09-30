"""Tests for reading/writing graphs (shared by shortest and longest path search)."""

import unittest

from dijkstra_app.core import GraphError
from dijkstra_app.graph_io import graph_to_edges, parse_edges
from tests.test_shortest import G


class ParsingTests(unittest.TestCase):
    def test_parse_formats(self):
        g = parse_edges("A B 2\nB->C:3.5\n# comment\nC,D,1\nZ\n")
        self.assertEqual(g["A"], {"B": 2})
        self.assertEqual(g["B"], {"C": 3.5})
        self.assertIn("Z", g)

    def test_parse_undirected(self):
        g = parse_edges("A B 2", directed=False)
        self.assertEqual(g["B"], {"A": 2})

    def test_parse_bad_lines(self):
        for bad in ("A B", "A B x", "A B -1", "A B 1 2"):
            with self.assertRaises(GraphError, msg=bad):
                parse_edges(bad)

    def test_edge_list_roundtrip(self):
        self.assertEqual(parse_edges(graph_to_edges(G)), G)


if __name__ == "__main__":
    unittest.main()
