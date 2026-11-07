"""
main_window.py (Member A)

Main window of the compiler UI and the program entry point.
Holds the toolbar, the editor, and the output panels, and connects the
buttons to the Scanner and to the panels.

Layout:
    Top    - toolbar: Open File, New File, Compile Code, Show Tokenized Code
    Left   - editor area (EditorPanel)
    Right  - tokenized code (TokenPanel) above table of variables (VariablePanel)
    Bottom - console (ConsolePanel) and a status bar

Run:
    python main_window.py
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ui_editor_panel import EditorPanel
from ui_token_panel import TokenPanel
from ui_console_panel import ConsolePanel
from ui_variable_panel import VariablePanel
from lex_scanner import Scanner


IOL_FILE_TYPES = [("IOL source files", "*.iol"), ("All files", "*.*")]


class MainWindow:

    def __init__(self, root):
        """Creates the window, the panels, and the toolbar."""
        self.root = root
        self.root.title("IOL Compiler - Lexical Analyzer")
        self.root.geometry("1100x700")

        # Lexical analyzer (Member B)
        self.scanner = Scanner()

        # Result of the most recent compile. None until Compile Code is clicked.
        self.last_result = None

        # Path of the file loaded in the editor. None for a new, unsaved file.
        self.current_file = None

        self.create_toolbar()
        self.create_status_bar()
        self.create_main_area()

        # Program ends only when the user closes the window
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def create_toolbar(self):
        """Builds the toolbar with the four main buttons."""
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="New File", command=self.new_file).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Compile Code", command=self.compile_code).pack(side=tk.LEFT, padx=(12, 2), pady=2)
        tk.Button(toolbar, text="Show Tokenized Code", command=self.show_tokenized_code).pack(side=tk.LEFT, padx=2, pady=2)

    def create_status_bar(self):
        """Builds the status bar shown at the bottom of the window."""
        self.status_bar = tk.Label(self.root, text=" Ready", anchor=tk.W, bd=1, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_main_area(self):
        """Builds the editor, output panels, and console using resizable panes."""
        # Whole area: top half above, console below
        main_area = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_area.pack(fill=tk.BOTH, expand=True)

        # Top half: editor on the left, output panels on the right
        top_half = ttk.PanedWindow(main_area, orient=tk.HORIZONTAL)

        # Right side: tokenized code on top, table of variables below
        right_side = ttk.PanedWindow(top_half, orient=tk.VERTICAL)

        self.editor_panel = EditorPanel(top_half)
        self.token_panel = TokenPanel(right_side)
        self.variable_panel = VariablePanel(right_side)
        self.console_panel = ConsolePanel(main_area)

        right_side.add(self.token_panel, weight=1)
        right_side.add(self.variable_panel, weight=1)

        top_half.add(self.editor_panel, weight=3)
        top_half.add(right_side, weight=2)

        main_area.add(top_half, weight=3)
        main_area.add(self.console_panel, weight=1)

    # ------------------------------------------------------------------
    # Button actions
    # ------------------------------------------------------------------

    def open_file(self):
        """
        Open File: lets the user pick an .iol file and loads it into the editor.
        The loaded content replaces whatever is in the editor.
        """
        path = filedialog.askopenfilename(title="Open File", filetypes=IOL_FILE_TYPES)
        if not path:
            return  # user cancelled

        try:
            content = self.read_file(path)
        except FileNotFoundError:
            self.show_error(f"File not found:\n{path}")
            return
        except (OSError, UnicodeDecodeError) as error:
            self.show_error(f"Unable to read file:\n{path}\n{error}")
            return

        self.editor_panel.set_text(content)
        self.current_file = path
        self.last_result = None  # previous compile result no longer matches the editor
        self.root.title(f"IOL Compiler - {os.path.basename(path)}")
        self.set_status(f"Opened {path}")

    def new_file(self):
        """
        New File: clears the editor for new code.
        Asks to save the current content first if the editor is not empty.
        """
        if self.editor_panel.get_text().strip() != "":
            # Returns True (Yes), False (No), or None (Cancel)
            answer = messagebox.askyesnocancel("New File", "Save the current code before creating a new file?")
            if answer is None:
                return
            if answer is True and not self.save_file():
                return  # save was cancelled or failed, keep the current code

        self.editor_panel.clear()
        self.current_file = None
        self.last_result = None
        self.root.title("IOL Compiler - Untitled")
        self.set_status("New file")

    def compile_code(self):
        """
        Compile Code: runs the Scanner on the current editor text, sends the
        results to the console and variable table, and writes the .tkn file.
        """
        # Always use what is in the editor right now
        source_code = self.editor_panel.get_text()

        if source_code.strip() == "":
            messagebox.showwarning("Compile Code", "The editor is empty. Open a file or type some code first.")
            return

        self.last_result = self.scanner.analyze(source_code)

        self.console_panel.show_result(self.last_result.errors)
        self.variable_panel.show_variables(self.last_result.variables)
        self.token_panel.show_tokens([])  # clear old tokens until Show Tokenized Code is clicked

        self.write_token_file(self.last_result.tokens)

    def show_tokenized_code(self):
        """Show Tokenized Code: displays the tokens from the last compile."""
        if self.last_result is None:
            messagebox.showinfo("Show Tokenized Code", "Compile the code first.")
            return
        self.token_panel.show_tokens(self.last_result.tokens)

    # ------------------------------------------------------------------
    # File helpers
    # ------------------------------------------------------------------

    def read_file(self, path):
        """Reads a whole text file and returns its content."""
        with open(path, "r", encoding="utf-8") as file:
            return file.read()

    def write_file(self, path, text):
        """Writes text to a file, replacing its old content."""
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)

    def save_file(self):
        """
        Saves the editor content to an .iol file chosen by the user.
        Returns True if the file was saved, False if cancelled or failed.
        """
        path = filedialog.asksaveasfilename(title="Save File", defaultextension=".iol", filetypes=IOL_FILE_TYPES)
        if not path:
            return False

        try:
            self.write_file(path, self.editor_panel.get_text())
        except OSError as error:
            self.show_error(f"Unable to save file:\n{path}\n{error}")
            return False

        self.set_status(f"Saved {path}")
        return True

    def write_token_file(self, tokens):
        """
        Writes the token stream to a .tkn file.
        Opened file "sample.iol" produces "sample.tkn" in the same folder.
        A new, unsaved file produces "untitled.tkn" in the program folder.
        """
        if self.current_file is not None:
            base_name = os.path.splitext(self.current_file)[0]
            token_path = base_name + ".tkn"
        else:
            token_path = os.path.abspath("untitled.tkn")

        try:
            self.write_file(token_path, self.build_token_stream(tokens))
        except OSError as error:
            self.show_error(f"Unable to write token file:\n{token_path}\n{error}")
            return

        self.set_status(f"Compiled. Token file saved to {token_path}")

    def build_token_stream(self, tokens):
        """
        Converts the token list to text. Each lexeme is replaced by its token
        name, and tokens stay on the same line number as in the source code.

        Example: source line "DEFINE x INTO" becomes "DEFINE IDENT INTO".
        """
        lines = []  # each item is the list of token names on one line

        for token in tokens:
            # Add empty lines until the token's line exists, keeping blank lines
            while len(lines) < token.line:
                lines.append([])
            lines[token.line - 1].append(token.type)

        text_lines = []
        for line_tokens in lines:
            text_lines.append(" ".join(line_tokens))

        return "\n".join(text_lines) + "\n"

    # ------------------------------------------------------------------
    # Message helpers
    # ------------------------------------------------------------------

    def show_error(self, message):
        """Shows an error dialog."""
        messagebox.showerror("Error", message)

    def set_status(self, message):
        """Updates the status bar text."""
        self.status_bar.config(text=" " + message)


def main():
    """Starts the program and opens the compiler UI."""
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
