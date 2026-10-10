"""Tokenized-code display for the compiler UI."""

import tkinter as tk


class TokenPanel(tk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, text="Tokenized Code (Member B)")
        self.text = tk.Text(self, state=tk.DISABLED)
        self.text.pack(fill=tk.BOTH, expand=True)

    def show_tokens(self, tokens):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        for token in tokens:
            self.text.insert(tk.END, f"{token.line}: {token.type}  {token.lexeme}\n")
        self.text.config(state=tk.DISABLED)
