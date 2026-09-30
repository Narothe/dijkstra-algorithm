"""Tkinter desktop app: type or load a graph, pick two vertices, see the result."""

from __future__ import annotations

import csv
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .longest import longest_path
from .core import INF, GraphError, format_number, steps_to_rows
from .shortest import shortest_path
from .graph_io import graph_to_edges, load_json, parse_edges, save_json
from .visualize import compute_layout, draw_graph

EXAMPLE = """\
# One edge per line:  FROM TO WEIGHT
A B 6
A C 1
A D 3
B F 4
C B 7
C E 6
C F 12
D B 2
D G 14
D E 3
D H 9
E F 4
F H 1
F I 5
G J 2
H G 3
H J 8
H I 2
I J 4
"""

HELP = (
    "One edge per line: FROM TO WEIGHT (e.g. A B 6).\n"
    "A lone name adds an isolated vertex. Lines starting with # are ignored."
)


class App(tk.Tk):
    def __init__(self, path: str | None = None):
        super().__init__()
        self.title("Dijkstra's Algorithm")
        self.geometry("1250x780")
        self.minsize(950, 600)

        self.graph: dict = {}
        self.result = None
        self.pos: dict | None = None
        self.path: list[str] | None = None
        self.directed = tk.BooleanVar(value=True)
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()
        self.step_var = tk.IntVar(value=0)
        self.mode = tk.StringVar(value="Shortest path")
        self.status = tk.StringVar(value="Enter a graph and press Calculate.")

        self._build()
        self.editor.insert("1.0", EXAMPLE)
        if path:
            self.load_file(path)
        self.calculate()

    # ---------- layout ----------
    def _build(self):
        left = ttk.Frame(self, padding=8)
        left.pack(side="left", fill="y")
        right = ttk.Frame(self, padding=(0, 8, 8, 8))
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Graph (edge list)", font=("", 11, "bold")).pack(anchor="w")
        ttk.Label(left, text=HELP, foreground="#555", wraplength=260).pack(anchor="w", pady=(0, 4))
        self.editor = tk.Text(left, width=32, height=22, font=("Consolas", 11), undo=True)
        self.editor.pack(fill="y", expand=True)

        ttk.Checkbutton(left, text="Directed edges", variable=self.directed,
                        command=self.calculate).pack(anchor="w", pady=4)

        files = ttk.Frame(left)
        files.pack(fill="x")
        for text, cmd in [("Open…", self.open_dialog), ("Save…", self.save_dialog),
                          ("Example", self.load_example), ("Clear", self.clear)]:
            ttk.Button(files, text=text, command=cmd, width=8).pack(side="left", padx=1)

        form = ttk.Frame(left)
        form.pack(fill="x", pady=8)
        ttk.Label(form, text="From").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="To").grid(row=1, column=0, sticky="w")
        self.start_box = ttk.Combobox(form, textvariable=self.start_var, state="readonly", width=10)
        self.end_box = ttk.Combobox(form, textvariable=self.end_var, state="readonly", width=10)
        self.start_box.grid(row=0, column=1, padx=6, pady=2)
        self.end_box.grid(row=1, column=1, padx=6, pady=2)
        for box in (self.start_box, self.end_box):
            box.bind("<<ComboboxSelected>>", lambda _e: self.calculate())

        ttk.Label(form, text="Find").grid(row=2, column=0, sticky="w")
        mode_box = ttk.Combobox(form, textvariable=self.mode, state="readonly", width=14,
                                values=["Shortest path", "Longest path"])
        mode_box.grid(row=2, column=1, padx=6, pady=2)
        mode_box.bind("<<ComboboxSelected>>", lambda _e: self.calculate())

        ttk.Button(left, text="Calculate  (Ctrl+Enter)", command=self.calculate).pack(fill="x")
        self.bind("<Control-Return>", lambda _e: self.calculate())

        # right: drawing + steps
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        nav = ttk.Frame(right)
        nav.pack(fill="x", pady=4)
        ttk.Button(nav, text="◀", width=3, command=lambda: self.move_step(-1)).pack(side="left")
        self.slider = ttk.Scale(nav, from_=0, to=0, orient="horizontal", command=self._on_slider)
        self.slider.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(nav, text="▶", width=3, command=lambda: self.move_step(1)).pack(side="left")
        ttk.Button(nav, text="Show final", command=self.show_final).pack(side="left", padx=(8, 0))
        ttk.Button(nav, text="Export table (CSV)", command=self.export_csv).pack(side="left", padx=4)
        ttk.Button(nav, text="Save image", command=self.save_image).pack(side="left")

        ttk.Label(right, textvariable=self.status, font=("", 11, "bold"),
                  wraplength=900).pack(anchor="w", pady=2)

        self.table = ttk.Treeview(right, show="headings", height=8)
        self.table.pack(fill="x")

    # ---------- graph input ----------
    def read_graph(self) -> dict:
        return parse_edges(self.editor.get("1.0", "end"), self.directed.get())

    def open_dialog(self):
        path = filedialog.askopenfilename(
            filetypes=[("Graph files", "*.json *.txt"), ("All files", "*.*")])
        if path:
            self.load_file(path)
            self.calculate()

    def load_file(self, path: str):
        try:
            if path.lower().endswith(".json"):
                graph, directed = load_json(path)
                self.directed.set(directed)
                text = graph_to_edges(graph, directed)
            else:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
        except (OSError, ValueError) as exc:
            messagebox.showerror("Cannot open file", str(exc))
            return
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", text)

    def save_dialog(self):
        try:
            graph = self.read_graph()
        except GraphError as exc:
            messagebox.showerror("Invalid graph", str(exc))
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Edge list", "*.txt")])
        if not path:
            return
        if path.lower().endswith(".json"):
            save_json(path, graph, self.directed.get())
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(graph_to_edges(graph, self.directed.get()) + "\n")

    def load_example(self):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", EXAMPLE)
        self.directed.set(True)
        self.start_var.set("")
        self.end_var.set("")
        self.calculate()

    def clear(self):
        self.editor.delete("1.0", "end")
        self.calculate()

    @property
    def kind(self) -> str:
        return "longest" if self.longest else "shortest"

    @property
    def longest(self) -> bool:
        return self.mode.get() == "Longest path"

    # ---------- calculation ----------
    def calculate(self):
        try:
            graph = self.read_graph()
        except GraphError as exc:
            self.status.set(f"⚠ {exc}")
            return
        if not graph:
            self.graph, self.result = {}, None
            self.ax.clear(); self.ax.set_axis_off(); self.canvas.draw_idle()
            self.table.delete(*self.table.get_children())
            self.status.set("Graph is empty.")
            return

        self.graph = graph
        names = sorted(graph)
        self.start_box["values"] = names
        self.end_box["values"] = names
        if self.start_var.get() not in graph:
            self.start_var.set(names[0])
        if self.end_var.get() not in graph:
            self.end_var.set(names[-1])

        try:
            solver = longest_path if self.longest else shortest_path
            self.result = solver(graph, self.start_var.get())
        except GraphError as exc:
            self.status.set(f"⚠ {exc}")
            return
        self.path = self.result.path_to(self.end_var.get())
        self.pos = compute_layout(graph, self.start_var.get(), self.directed.get())

        self.fill_table()
        last = len(self.result.steps) - 1
        self.slider.configure(to=last)
        self.show_final()

        start, end = self.start_var.get(), self.end_var.get()
        if self.path is None:
            self.status.set(f"No path from {start} to {end}.")
        else:
            cost = format_number(self.result.distances[end])
            kind = "Longest" if self.longest else "Shortest"
            note = "  [DAG: exact, linear time]" if self.result.method == "dag" else (
                "  [graph has cycles: exhaustive search of simple paths]" if self.longest else "")
            self.status.set(f"{kind} path {start} → {end}:  {' → '.join(self.path)}   "
                            f"({'length' if self.longest else 'cost'} {cost}){note}")

    def fill_table(self):
        header, rows = steps_to_rows(self.result, self.graph)
        self.table.delete(*self.table.get_children())
        self.table["columns"] = header
        for i, name in enumerate(header):
            self.table.heading(name, text=name)
            self.table.column(name, width=70 if i != 1 else 170, anchor="center", stretch=True)
        for row in rows:
            self.table.insert("", "end", values=row)

    # ---------- step navigation ----------
    def render(self, step_index: int | None):
        """step_index None -> final view with path highlighted."""
        if not self.result:
            return
        if step_index is None:
            step = self.result.steps[-1]
            path, title = self.path, f"{'Longest' if self.longest else 'Shortest'} path highlighted in red"
        else:
            step = self.result.steps[step_index]
            path = None
            title = f"Stage {step.number}" + (f": vertex {step.current} finalised" if step.current else "")
        draw_graph(self.ax, self.graph, self.directed.get(), pos=self.pos, path=path,
                   visited=step.visited, current=step.current if step_index is not None else None,
                   distances=step.distances, title=title)
        self.figure.tight_layout()
        self.canvas.draw_idle()
        items = self.table.get_children()
        idx = len(items) - 1 if step_index is None else step_index
        if items:
            self.table.selection_set(items[idx])
            self.table.see(items[idx])

    def _on_slider(self, value):
        if self.result:
            self.step_var.set(round(float(value)))
            self.render(self.step_var.get())

    def move_step(self, delta: int):
        if not self.result:
            return
        new = min(max(self.step_var.get() + delta, 0), len(self.result.steps) - 1)
        self.step_var.set(new)
        self.slider.set(new)
        self.render(new)

    def show_final(self):
        if self.result:
            self.step_var.set(len(self.result.steps) - 1)
            self.slider.set(len(self.result.steps) - 1)
            self.render(None)

    # ---------- export ----------
    def export_csv(self):
        if not self.result:
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            initialfile=f"{self.kind}_path_table.csv", filetypes=[("CSV", "*.csv")])
        if path:
            header, rows = steps_to_rows(self.result, self.graph)
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerows([header] + rows)

    def save_image(self):
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            initialfile=f"{self.kind}_path.png",
                                            filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
        if path:
            self.figure.savefig(path, dpi=200)


def run(path: str | None = None):
    App(path).mainloop()
