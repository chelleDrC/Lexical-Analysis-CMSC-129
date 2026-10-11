"""
ui_variable_panel.py (Member D: Mark Jaily Pena)

Table of variables panel for the IOL compiler UI.
Displays a table listing declared identifiers and their corresponding data types
(e.g., INT or STR) with guaranteed duplicate suppression.

Shared contract:
    MainWindow uses: VariablePanel(parent)
    MainWindow calls: show_variables(variables)
"""

import tkinter as tk
from tkinter import ttk


class VariablePanel(tk.LabelFrame):
    """UI panel that displays a table of variables (identifier name and type)."""

    def __init__(self, parent):
        """Initializes the table of variables panel with a Treeview and scrollbar."""
        super().__init__(parent, text="Table of Variables")

        # Scrollbar for viewing lists of variables
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview table with two columns: Variable Name and Data Type
        self.table = ttk.Treeview(
            self,
            columns=("name", "type"),
            show="headings",
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.table.yview)

        # Configure column headings
        self.table.heading("name", text="Variable Name", anchor=tk.W)
        self.table.heading("type", text="Data Type", anchor=tk.CENTER)

        # Configure column widths and alignments
        self.table.column("name", width=140, minwidth=80, anchor=tk.W)
        self.table.column("type", width=90, minwidth=60, anchor=tk.CENTER)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_variables(self, variables):
        """
        Populates the variable table with the provided variables.
        Replaces existing entries and prevents duplicate identifier names.

        Args:
            variables: List of Variable objects (each having .name and .type)
                       or iterable of (name, type) pairs.
        """
        self.clear()

        if not variables:
            return

        seen_names = set()
        for variable in variables:
            # Extract name and type from Variable object, dict, or tuple
            if hasattr(variable, "name") and hasattr(variable, "type"):
                var_name = variable.name
                var_type = variable.type
            elif isinstance(variable, dict):
                var_name = variable.get("name")
                var_type = variable.get("type")
            elif isinstance(variable, (list, tuple)) and len(variable) >= 2:
                var_name = variable[0]
                var_type = variable[1]
            else:
                continue

            # Ensure each identifier appears only once (no duplicates)
            if var_name and var_name not in seen_names:
                seen_names.add(var_name)
                self.table.insert("", tk.END, values=(var_name, var_type))

    def clear(self):
        """Clears all rows from the variable table."""
        for row in self.table.get_children():
            self.table.delete(row)

    def get_variables(self):
        """
        Returns the list of (name, type) tuples currently shown in the table.
        Useful for verification and automated tests.
        """
        result = []
        for row_id in self.table.get_children():
            values = self.table.item(row_id, "values")
            if values:
                result.append((values[0], values[1]))
        return result

    def count(self):
        """Returns the number of unique variables currently in the table."""
        return len(self.table.get_children())
