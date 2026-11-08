"""Controller for the PE03 predictive parser (Member 4).

Connects the View (Member 3) to the file loaders and checks (Member 1),
the parser (Member 2), and the output writer (PrsdWriter).

The controller keeps the currently loaded productions and parse table. A
file is stored only after it loads successfully, so a failed or cancelled
load leaves the previous file in use.
"""

import os
from tkinter import messagebox

from file_validation import PROD_EXT, LoadError, check_pair, file_type
from parse_data import ParseResult, ParseTable, Production
from parse_table_loader import ParseTableLoader
from parser import PredictiveParser
from production_loader import ProductionLoader
from prsd_writer import PrsdWriter
from view import View


class Controller:

    def __init__(self, view: View) -> None:
        self.view = view

        self.productions: list[Production] | None = None
        self.prod_path: str | None = None
        self.table: ParseTable | None = None
        self.ptbl_path: str | None = None

        # Set after each successful load: why the loaded pair cannot be used
        # together, or None when both files are loaded and compatible.
        self.pair_problem: str | None = None

        view.set_on_load(self.on_load)
        view.set_on_parse(self.on_parse)
        view.set_on_input_change(self.on_input_change)
        view.set_parse_enabled(False)

    # ----- Load -------------------------------------------------------------

    def on_load(self) -> None:
        """Load one .prod or .ptbl file chosen by the user."""
        path = self.view.choose_file()
        if not path:
            return  # Cancelled: keep the files that are already loaded.

        # Every real load attempt clears the old solution first.
        self.view.clear_solution_table()
        self.view.set_parsing_message("")

        try:
            if file_type(path) == PROD_EXT:
                self._load_productions(path)
            else:
                self._load_table(path)
        except LoadError as error:
            messagebox.showerror("Cannot load file", str(error), parent=self.view.root)
            return

        self.pair_problem = self._check_pair()
        self.view.set_parsing_message(self.pair_problem or "")
        self.view.set_parse_enabled(self._can_parse(self.view.get_input_text()))

    def _load_productions(self, path: str) -> None:
        productions = ProductionLoader.load(path)  # Raises LoadError on failure.
        self.productions = productions
        self.prod_path = path
        name = os.path.basename(path)
        self.view.set_productions(productions, name)
        self.view.set_loaded_message(name)

    def _load_table(self, path: str) -> None:
        table = ParseTableLoader.load(path)  # Raises LoadError on failure.
        self.table = table
        self.ptbl_path = path
        name = os.path.basename(path)
        self.view.set_parse_table(table, name)
        self.view.set_loaded_message(name)

    def _check_pair(self) -> str | None:
        """Return why the loaded files cannot be used together, or None."""
        if self.productions is None or self.table is None:
            return None  # Only one file loaded so far: nothing to compare yet.
        try:
            check_pair(self.prod_path, self.productions, self.ptbl_path, self.table)
        except LoadError as error:
            return f"Cannot parse: {error}"
        return None

    # ----- Input and Parse --------------------------------------------------

    def _can_parse(self, text: str) -> bool:
        """Parse needs both files loaded, compatible, and a non-empty input."""
        return (
            self.productions is not None
            and self.table is not None
            and self.pair_problem is None
            and bool(text.strip())
        )

    def on_input_change(self, text: str) -> None:
        self.view.set_parse_enabled(self._can_parse(text))

    def on_parse(self) -> None:
        text = self.view.get_input_text()
        if not self._can_parse(text):
            return

        result = PredictiveParser.parse(self.productions, self.table, text)
        self.view.show_solution_rows(result.steps)
        self._save_result(result)

    def _save_result(self, result: ParseResult) -> None:
        """Ask for an output name, save the steps, and show the outcome."""
        outcome = "Valid" if result.valid else "Invalid"

        outname = PrsdWriter.ask_output_name(self.prod_path, self.view.root)
        if outname is None:
            self.view.set_parsing_message(f"PARSING: {outcome}. Output was not saved.")
            return

        try:
            path = PrsdWriter.write(result, outname, self.prod_path)
        except OSError as error:
            message = f"Could not save the output file: {error.strerror or error}."
            messagebox.showerror("Save failed", message, parent=self.view.root)
            self.view.set_parsing_message(f"PARSING: {outcome}. {message}")
            return

        self.view.set_parsing_message(
            f"PARSING: {outcome}. Please see {os.path.basename(path)}."
        )
