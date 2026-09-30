"""Dijkstra's algorithm: solver, step table, and visual app."""

__version__ = "2.0.0"

from .core import Result, format_table  # noqa: E402,F401
from .shortest import dijkstra, shortest_path  # noqa: E402,F401
from .longest import longest_path  # noqa: E402,F401
