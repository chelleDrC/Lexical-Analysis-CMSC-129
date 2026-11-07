"""Tokenized-code display for the compiler UI."""

import tkinter as tk


class TokenPanel(tk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, text="Tokenized Code")

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self, state=tk.DISABLED, yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.text.yview)

    def show_tokens(self, tokens):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        for token in tokens:
            self.text.insert(tk.END, f"{token.line}: {token.type}  {token.lexeme}\n")
        self.text.config(state=tk.DISABLED)
