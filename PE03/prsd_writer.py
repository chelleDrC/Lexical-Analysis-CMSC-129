"""Asks for an output name and saves the parse steps as a .prsd CSV file (Member 4)."""

import csv
import os
from tkinter import messagebox, simpledialog

from file_validation import base_name
from parse_data import ParseResult

PRSD_EXT = ".prsd"

# Characters Windows does not allow in file names.
_INVALID_NAME_CHARS = set('<>:"/\\|?*')


class PrsdWriter:

    @staticmethod
    def output_path(outname: str, prod_path: str) -> str:
        """Return ``<folder>/outname_prodname.prsd``, in the productions file's folder.

        Example: outname ``test`` with ``C:/work/rules.prod`` gives
        ``C:/work/test_rules.prsd``.
        """
        folder = os.path.dirname(prod_path)
        file_name = f"{outname}_{base_name(prod_path)}{PRSD_EXT}"
        return os.path.join(folder, file_name)

    @staticmethod
    def ask_output_name(prod_path: str, parent) -> str | None:
        """Ask the user for a valid output name. Return None if they cancel.

        Asks again when the name is empty, has forbidden characters, or the
        user refuses to overwrite an existing file.
        """
        while True:
            name = simpledialog.askstring(
                "Output name",
                "Enter a name for the output file:",
                parent=parent,
            )
            if name is None:
                return None

            name = name.strip()
            if not name or any(c in _INVALID_NAME_CHARS or ord(c) < 32 for c in name):
                messagebox.showerror(
                    "Invalid name",
                    "Use a name without any of these characters: < > : \" / \\ | ? *",
                    parent=parent,
                )
                continue

            path = PrsdWriter.output_path(name, prod_path)
            if os.path.exists(path) and not messagebox.askyesno(
                "Replace file?",
                f"{os.path.basename(path)} already exists. Replace it?",
                parent=parent,
            ):
                continue
            return name

    @staticmethod
    def write(result: ParseResult, outname: str, prod_path: str) -> str:
        """Write the parse steps as CSV rows and return the saved file's path.

        Each row is: stack, input buffer, action. The csv module quotes any
        field that contains a comma. Raises OSError if the file cannot be written.
        """
        path = PrsdWriter.output_path(outname, prod_path)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for step in result.steps:
                writer.writerow([step.stack, step.input, step.action])
        return path
