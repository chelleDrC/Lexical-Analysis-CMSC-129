"""
ui_console_panel.py (Member C)

PLACEHOLDER - replace this file with Member C's version.
main_window.py uses: show_result(errors)

Displays the success message or the list of lexical errors.
"""

import tkinter as tk


class ConsolePanel(tk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, text="Console (Member C)")
        self.text = tk.Text(self, height=6, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)

    def show_result(self, errors):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        if len(errors) == 0:
            self.text.insert(tk.END, "Lexical analysis successful. No errors found.\n")
        else:
            for error in errors:
                self.text.insert(tk.END, f"Unknown word '{error.lexeme}' at line {error.line}\n")
        self.text.config(state=tk.DISABLED)
