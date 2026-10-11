"""Console panel for lexical-analysis success and error messages."""

import tkinter as tk


class ConsolePanel(tk.LabelFrame):

    def __init__(self, parent):
        super().__init__(parent, text="Console")
        self.text = tk.Text(self, height=6, state=tk.DISABLED, wrap=tk.WORD)
        self.text.tag_configure("success", foreground="#1b7f3a")
        self.text.tag_configure("error", foreground="#b00020")
        self.text.tag_configure("heading", font=("TkDefaultFont", 9, "bold"))
        self.text.pack(fill=tk.BOTH, expand=True)

    def show_result(self, errors):
        self.text.config(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)

        messages = self.build_messages(errors)
        if len(errors) == 0:
            self.text.insert(tk.END, messages[0] + "\n", "success")
        else:
            self.text.insert(tk.END, messages[0] + "\n", ("heading", "error"))
            for message in messages[1:]:
                self.text.insert(tk.END, message + "\n", "error")

        self.text.config(state=tk.DISABLED)

    @staticmethod
    def build_messages(errors):
        if len(errors) == 0:
            return ["Lexical analysis successful. No lexical errors found."]

        messages = [f"Lexical analysis failed. Found {len(errors)} lexical error(s):"]
        for error in errors:
            messages.append(f"ERR_LEX: unknown word '{error.lexeme}' at line {error.line}")
        return messages
