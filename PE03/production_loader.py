"""Loads a .prod file into a list of Production objects (Member 1).

Each row is: line number, non-terminal, production.
Example: ``2,E',+ T E'``. The empty production is written as ``e``.
"""

import os

from csv_reader import CsvReader
from file_validation import PROD_EXT, LoadError, check_extension, normalize_symbol
from parse_data import EMPTY_SYMBOL, Production


class ProductionLoader:

    @staticmethod
    def load(path: str) -> list[Production]:
        """Read and validate ``path``. Raises LoadError with a clear message."""
        check_extension(path, PROD_EXT)
        name = os.path.basename(path)

        productions = []
        seen_ids = set()
        for line, cells in CsvReader.read_rows(path):
            where = f"{name}, line {line}"
            production = ProductionLoader.parse_row(cells, where)
            if production.id in seen_ids:
                raise LoadError(
                    f"{where}: production number {production.id} is used twice."
                )
            seen_ids.add(production.id)
            productions.append(production)

        if 1 not in seen_ids:
            raise LoadError(
                f"{name}: there is no production 1. Production 1 gives the "
                f"start symbol."
            )
        return productions

    @staticmethod
    def start_symbol(productions: list[Production]) -> str:
        """The non-terminal of production 1."""
        return next(p.non_terminal for p in productions if p.id == 1)

    @staticmethod
    def parse_row(cells: list[str], where: str) -> Production:
        # Drop empty cells after the third column (trailing commas). A blank
        # third column is kept so it is reported as an empty production.
        while len(cells) > 3 and not cells[-1].strip():
            cells = cells[:-1]

        if len(cells) < 3:
            raise LoadError(
                f"{where}: missing columns. Expected 3 columns "
                f"(number, non-terminal, production), found {len(cells)}."
            )
        if len(cells) > 3:
            raise LoadError(
                f"{where}: too many columns. Expected 3 columns "
                f"(number, non-terminal, production), found {len(cells)}."
            )

        number_text, nt_text, rhs_text = cells

        number_text = number_text.strip()
        try:
            number = int(number_text)
        except ValueError:
            raise LoadError(
                f"{where}: production number '{number_text}' is not a whole number."
            ) from None
        if number < 1:
            raise LoadError(f"{where}: production number must be 1 or higher.")

        non_terminal = normalize_symbol(nt_text)
        if not non_terminal:
            raise LoadError(f"{where}: non-terminal is empty.")
        if len(non_terminal.split()) > 1:
            raise LoadError(
                f"{where}: non-terminal '{non_terminal}' must be one symbol."
            )

        symbols = [normalize_symbol(s) for s in rhs_text.split()]
        if not symbols:
            raise LoadError(
                f"{where}: production is empty. Use {EMPTY_SYMBOL} for the "
                f"empty production."
            )
        if EMPTY_SYMBOL in symbols:
            if len(symbols) > 1:
                raise LoadError(
                    f"{where}: {EMPTY_SYMBOL} (empty) must be the only symbol "
                    f"in its production."
                )
            symbols = []

        return Production(number, non_terminal, symbols)
