"""Loads a .ptbl file into a ParseTable (Member 1).

The first row holds the terminals plus ``$``, after an empty top-left cell:
``,id,+,*,(,),$``. Each other row is a non-terminal followed by one cell per
terminal. A cell is a production number or blank.
"""

import os

from csv_reader import CsvReader
from file_validation import PTBL_EXT, LoadError, check_extension, normalize_symbol
from parse_data import END_MARKER, ParseTable


def _trim_trailing_blanks(cells: list[str]) -> list[str]:
    while cells and not cells[-1].strip():
        cells = cells[:-1]
    return cells


class ParseTableLoader:

    @staticmethod
    def load(path: str) -> ParseTable:
        """Read and validate ``path``. Raises LoadError with a clear message."""
        check_extension(path, PTBL_EXT)
        name = os.path.basename(path)

        rows = CsvReader.read_rows(path)
        header_line, header = rows[0]
        terminals = ParseTableLoader.parse_header(header, f"{name}, line {header_line}")

        result = ParseTable(terminals=terminals)
        for line, cells in rows[1:]:
            where = f"{name}, line {line}"
            non_terminal, row = ParseTableLoader.parse_row(cells, terminals, where)
            if non_terminal in result.table:
                raise LoadError(f"{where}: non-terminal {non_terminal} has two rows.")
            result.non_terminals.append(non_terminal)
            result.table[non_terminal] = row

        if not result.non_terminals:
            raise LoadError(f"{name}: parse table has no non-terminal rows.")
        return result

    @staticmethod
    def parse_header(cells: list[str], where: str) -> list[str]:
        # The top-left cell is the label of the non-terminal column. It is
        # normally empty and is ignored either way.
        cells = _trim_trailing_blanks(cells)
        terminals = [normalize_symbol(c) for c in cells[1:]]

        if not terminals:
            raise LoadError(
                f"{where}: missing columns. The first row must list the "
                f"terminals and {END_MARKER}, e.g. ,id,+,{END_MARKER}"
            )
        for i, t in enumerate(terminals, start=2):
            if not t:
                raise LoadError(f"{where}: column {i} has no terminal name.")
            if len(t.split()) > 1:
                raise LoadError(f"{where}: column {i} terminal '{t}' must be one symbol.")
        duplicates = sorted({t for t in terminals if terminals.count(t) > 1})
        if duplicates:
            raise LoadError(
                f"{where}: terminal(s) listed twice: {', '.join(duplicates)}."
            )
        if END_MARKER not in terminals:
            raise LoadError(
                f"{where}: missing the end marker column {END_MARKER}."
            )
        return terminals

    @staticmethod
    def parse_row(cells: list[str], terminals: list[str],
                  where: str) -> tuple[str, dict[str, int]]:
        cells = _trim_trailing_blanks(cells)
        non_terminal = normalize_symbol(cells[0]) if cells else ""
        if not non_terminal:
            raise LoadError(f"{where}: non-terminal is empty.")
        if len(non_terminal.split()) > 1:
            raise LoadError(f"{where}: non-terminal '{non_terminal}' must be one symbol.")

        values = cells[1:]
        if len(values) > len(terminals):
            raise LoadError(
                f"{where}: too many columns. Found {len(values)} cells but "
                f"the first row has {len(terminals)} terminals."
            )

        # A short row means its last cells are blank (trailing commas left out).
        row = {}
        for terminal, text in zip(terminals, values):
            text = text.strip()
            if not text:
                continue
            try:
                number = int(text)
            except ValueError:
                raise LoadError(
                    f"{where}: cell [{non_terminal}, {terminal}] is '{text}'. "
                    f"A cell must be a production number or blank."
                ) from None
            if number < 1:
                raise LoadError(
                    f"{where}: cell [{non_terminal}, {terminal}] must be 1 or higher."
                )
            row[terminal] = number
        return non_terminal, row
