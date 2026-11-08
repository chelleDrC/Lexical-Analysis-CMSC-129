"""Tkinter view for the PE03 predictive parser (Member 3)."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Iterable, Sequence
from tkinter import filedialog, ttk
from typing import Any

from parse_data import ParseStep, ParseTable, Production


class View:
    """Build the application window and expose view operations to a controller.

    The view owns widgets and presentation state only. Loading, validation,
    parsing, and saving results remain responsibilities of the controller.
    """

    def __init__(self, root: tk.Tk | None = None) -> None:
        self.root = root or tk.Tk()
        self.root.title("PE03 - Predictive Parser")
        self.root.geometry("1060x760")
        self.root.minsize(760, 520)

        self._load_listener: Callable[[], Any] | None = None
        self._parse_listener: Callable[[], Any] | None = None
        self._input_listener: Callable[[str], Any] | None = None
        self._input_trace_id: str | None = None

        self._configure_style()
        self._build_widgets()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("TkDefaultFont", 11, "bold"))
        style.configure("Status.TLabel", font=("TkDefaultFont", 10))
        style.configure("Treeview", rowheight=24)
        style.configure("Treeview.Heading", font=("TkDefaultFont", 9, "bold"))

    def _build_widgets(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.main = ttk.Frame(self.root, padding=10)
        self.main.grid(row=0, column=0, sticky="nsew")
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(3, weight=1)

        tables = ttk.Frame(self.main)
        tables.grid(row=0, column=0, sticky="nsew")
        tables.columnconfigure(0, weight=1, uniform="top_tables")
        tables.columnconfigure(1, weight=1, uniform="top_tables")

        self.productions_tree = self._make_tree(
            tables,
            row=1,
            column=0,
            columns=("id", "non_terminal", "rhs"),
            headings=("ID", "NT", "P"),
            widths=(48, 68, 170),
            anchors=(tk.CENTER, tk.CENTER, tk.W),
            title="Productions:",
        )
        self.productions_title = self.productions_tree.master.winfo_children()[0]
        self.parse_tree = self._make_tree(
            tables,
            row=1,
            column=1,
            columns=("non_terminal",),
            headings=("",),
            widths=(62,),
            anchors=(tk.CENTER,),
            title="Parse Table:",
        )
        self.parse_title = self.parse_tree.master.winfo_children()[0]

        load_row = ttk.Frame(self.main)
        load_row.grid(row=1, column=0, sticky="ew", pady=(5, 10))
        load_row.columnconfigure(1, weight=1)
        self.loaded_var = tk.StringVar(value="")
        ttk.Label(load_row, text="LOADED:", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=(4, 5)
        )
        self.loaded_label = ttk.Label(
            load_row, textvariable=self.loaded_var, style="Status.TLabel"
        )
        self.loaded_label.grid(row=0, column=1, sticky="w")
        self.load_button = ttk.Button(load_row, text="Load", command=self._on_load)
        self.load_button.grid(row=0, column=2, sticky="e", padx=(8, 4))

        input_row = ttk.Frame(self.main)
        input_row.grid(row=2, column=0, sticky="ew", pady=(0, 7))
        input_row.columnconfigure(1, weight=1)
        ttk.Label(input_row, text="INPUT", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=(4, 8)
        )
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_row, textvariable=self.input_var)
        self.input_entry.grid(row=0, column=1, sticky="ew", ipady=5)
        self.parse_button = ttk.Button(
            input_row, text="Parse", command=self._on_parse, state=tk.DISABLED
        )
        self.parse_button.grid(row=0, column=2, sticky="e", padx=(8, 4))
        self._input_trace_id = self.input_var.trace_add("write", self._on_input_change)

        status_row = ttk.Frame(self.main)
        status_row.grid(row=3, column=0, sticky="nsew")
        status_row.columnconfigure(0, weight=1)
        status_row.rowconfigure(1, weight=1)
        self.parsing_var = tk.StringVar(value="")
        self.parsing_label = ttk.Label(
            status_row, textvariable=self.parsing_var, style="Status.TLabel", wraplength=950
        )
        self.parsing_label.grid(row=0, column=0, sticky="w", padx=4, pady=(0, 5))
        status_row.bind("<Configure>", self._resize_parsing_message)
        self.solution_tree = self._make_tree(
            status_row,
            row=1,
            column=0,
            columns=("stack", "input", "action"),
            headings=("Stack", "Input Buffer", "Action"),
            widths=(200, 230, 370),
            anchors=(tk.E, tk.W, tk.W),
            title=None,
            stretch=(True, True, True),
        )
        self.solution_tree.heading("stack", anchor=tk.E)
        self.solution_tree.column("stack", anchor=tk.E)

    def _resize_parsing_message(self, event: tk.Event) -> None:
        self.parsing_label.configure(wraplength=max(100, event.width - 12))

    def _make_tree(
        self,
        parent: tk.Misc,
        *,
        row: int,
        column: int,
        columns: Sequence[str],
        headings: Sequence[str],
        widths: Sequence[int],
        anchors: Sequence[str],
        title: str | None,
        stretch: Sequence[bool] | None = None,
    ) -> ttk.Treeview:
        """Create a labeled Treeview with scrollbars and configurable columns."""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=column, sticky="nsew", padx=(3, 6) if column == 0 else (6, 3))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1 if title else 0, weight=1)
        tree_row = 1 if title else 0
        if title:
            ttk.Label(frame, text=title, style="Title.TLabel").grid(
                row=0, column=0, sticky="w", pady=(0, 2)
            )

        tree = ttk.Treeview(frame, columns=tuple(columns), show="headings", selectmode="browse")
        y_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        tree.grid(row=tree_row, column=0, sticky="nsew")
        y_scroll.grid(row=tree_row, column=1, sticky="ns")
        x_scroll.grid(row=tree_row + 1, column=0, sticky="ew")

        for index, column_id in enumerate(columns):
            tree.heading(column_id, text=headings[index], anchor=anchors[index])
            tree.column(
                column_id,
                width=widths[index],
                minwidth=36,
                anchor=anchors[index],
                stretch=stretch[index] if stretch else True,
            )
        return tree

    def _on_load(self) -> None:
        if self._load_listener:
            self._load_listener()

    def _on_parse(self) -> None:
        if self._parse_listener:
            self._parse_listener()

    def _on_input_change(self, *_: object) -> None:
        if self._input_listener:
            self._input_listener(self.get_input_text())

    def set_on_load(self, listener: Callable[[], Any] | None) -> None:
        """Register or remove the Load button listener."""
        self._load_listener = listener

    def set_on_parse(self, listener: Callable[[], Any] | None) -> None:
        """Register or remove the Parse button listener."""
        self._parse_listener = listener

    def set_on_input_change(self, listener: Callable[[str], Any] | None) -> None:
        """Register or remove a listener called with the current input text."""
        self._input_listener = listener

    def get_input_text(self) -> str:
        """Return the current input field value."""
        return self.input_var.get()

    def choose_file(self) -> str:
        """Open the shared .prod/.ptbl file picker; return an empty string on cancel."""
        return filedialog.askopenfilename(
            parent=self.root,
            title="Load productions or parse table",
            filetypes=(
                ("PE03 input files", ("*.prod", "*.ptbl")),
                ("Production files", "*.prod"),
                ("Parse table files", "*.ptbl"),
                ("All files", "*.*"),
            ),
        )

    @staticmethod
    def _replace_rows(tree: ttk.Treeview, rows: Iterable[Sequence[Any]]) -> None:
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", tk.END, values=tuple(row))

    def set_productions(
        self, productions: Iterable[Production], filename: str | None = None
    ) -> None:
        """Display production ID, left-hand side, and right-hand side rows."""
        self._replace_rows(
            self.productions_tree,
            ((p.id, p.non_terminal, p.rhs_text) for p in productions),
        )
        if filename is not None:
            self.productions_title.configure(text=f"Productions: {filename}")

    def set_parse_table(
        self, table: ParseTable, filename: str | None = None
    ) -> None:
        """Display a parse table, retaining blank cells as visibly empty cells."""
        columns = tuple(f"terminal_{index}" for index in range(len(table.terminals)))
        all_columns = ("non_terminal", *columns)
        self.parse_tree.configure(columns=all_columns)
        self.parse_tree.heading("non_terminal", text="", anchor=tk.CENTER)
        self.parse_tree.column("non_terminal", width=62, minwidth=48, anchor=tk.CENTER, stretch=False)
        for index, (column_id, terminal) in enumerate(zip(columns, table.terminals)):
            self.parse_tree.heading(column_id, text=terminal, anchor=tk.CENTER)
            self.parse_tree.column(
                column_id,
                width=max(48, min(94, len(terminal) * 12 + 26)),
                minwidth=36,
                anchor=tk.CENTER,
                stretch=True,
            )
        self._replace_rows(
            self.parse_tree,
            (
                (non_terminal, *(table.cell_text(non_terminal, terminal) for terminal in table.terminals))
                for non_terminal in table.non_terminals
            ),
        )
        if filename is not None:
            self.parse_title.configure(text=f"Parse Table: {filename}")

    def set_loaded_message(self, message: str) -> None:
        """Set the text displayed after the LOADED label."""
        self.loaded_var.set(message)

    def set_parsing_message(self, message: str) -> None:
        """Set the PARSING status or result message."""
        self.parsing_var.set(message)

    @staticmethod
    def _step_values(row: ParseStep | Sequence[Any]) -> tuple[Any, Any, Any]:
        if isinstance(row, ParseStep):
            return row.stack, row.input, row.action
        if len(row) != 3:
            raise ValueError("Each solution row must contain stack, input, and action.")
        return row[0], row[1], row[2]

    def show_solution_rows(self, rows: Iterable[ParseStep | Sequence[Any]]) -> None:
        """Replace the solution table with parser steps or three-value rows."""
        self._replace_rows(self.solution_tree, (self._step_values(row) for row in rows))

    def clear_solution_table(self) -> None:
        """Remove all currently displayed solution rows."""
        self.solution_tree.delete(*self.solution_tree.get_children())

    def set_parse_enabled(self, enabled: bool) -> None:
        """Enable or disable the Parse button based on controller state."""
        self.parse_button.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def run(self) -> None:
        """Start Tkinter's event loop."""
        self.root.mainloop()

    def close(self) -> None:
        """Destroy the application window."""
        if self._input_trace_id:
            self.input_var.trace_remove("write", self._input_trace_id)
            self._input_trace_id = None
        self.root.destroy()


if __name__ == "__main__":
    View().run()
