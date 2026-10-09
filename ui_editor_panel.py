"""
ui_editor_panel.py (Member A)

Editor area of the compiler UI. Holds the text box where the source code
is typed or loaded from a file.
"""

import tkinter as tk


class EditorPanel(tk.LabelFrame):

    def __init__(self, parent):
        """Creates the text box with a vertical scrollbar."""
        super().__init__(parent, text="Editor")

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self, font=("Courier New", 12), undo=True, wrap=tk.NONE,
                            yscrollcommand=scrollbar.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.text.yview)

    def get_text(self):
        """Returns the current text in the editor."""
        # "end-1c" leaves out the extra newline that Tkinter adds at the end
        return self.text.get("1.0", "end-1c")

    def set_text(self, content):
        """Replaces the editor content with the given text and moves the cursor to the top."""
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.see("1.0")

    def clear(self):
        """Removes all text from the editor."""
        self.text.delete("1.0", tk.END)
