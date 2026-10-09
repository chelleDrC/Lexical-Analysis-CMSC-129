"""
ui_variable_panel.py (Member D)

PLACEHOLDER - replace this file with Member D's version.
main_window.py uses: show_variables(variables)

Displays the table of variables (name and type).
"""

import tkinter as tk
from tkinter import ttk


class VariablePanel(tk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, text="Table of Variables (Member D)")
        self.table = ttk.Treeview(self, columns=("name", "type"), show="headings")
        self.table.heading("name", text="Name")
        self.table.heading("type", text="Type")
        self.table.pack(fill=tk.BOTH, expand=True)

    def show_variables(self, variables):
        for row in self.table.get_children():
            self.table.delete(row)
        for variable in variables:
            self.table.insert("", tk.END, values=(variable.name, variable.type))
