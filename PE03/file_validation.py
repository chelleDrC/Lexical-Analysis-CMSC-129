"""Shared checks used by the loaders and by the Controller (Member 1)."""

import os

from parse_data import END_MARKER, ParseTable, Production

PROD_EXT = ".prod"
PTBL_EXT = ".ptbl"

# Curly quotes, primes, and accents that should all mean a plain apostrophe.
_APOSTROPHES = {
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201b": "'",  # single high-reversed-9 quote
    "\u2032": "'",  # prime
    "\u00b4": "'",  # acute accent
    "`": "'",
}
_APOSTROPHE_TABLE = str.maketrans(_APOSTROPHES)


class LoadError(Exception):
    """Raised when a .prod or .ptbl file cannot be used.

    ``str(error)`` is a message that can be shown to the user as is.
    """


def normalize_symbol(text: str) -> str:
    """Strip spaces and turn curly apostrophes into ``'``.

    Member 2's Tokenizer should call this on input tokens too, so ``E’`` in
    the input matches ``E'`` in the files.
    """
    return text.translate(_APOSTROPHE_TABLE).strip()


def file_type(path: str) -> str:
    """Return ``PROD_EXT`` or ``PTBL_EXT`` for ``path``, by extension.

    Raises LoadError for any other extension.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (PROD_EXT, PTBL_EXT):
        return ext
    name = os.path.basename(path)
    raise LoadError(
        f"{name}: unsupported file type. Load a {PROD_EXT} or {PTBL_EXT} file."
    )


def check_extension(path: str, expected: str) -> None:
    """Raise LoadError if ``path`` does not end in ``expected``."""
    if os.path.splitext(path)[1].lower() != expected:
        name = os.path.basename(path)
        raise LoadError(f"{name}: expected a {expected} file.")


def base_name(path: str) -> str:
    """File name without folder and extension: ``C:/x/rules.prod`` -> ``rules``."""
    return os.path.splitext(os.path.basename(path))[0]


def names_match(prod_path: str, ptbl_path: str) -> bool:
    """True when both files have the same name, e.g. rules.prod and rules.ptbl.

    The comparison ignores case, because Windows file names are not case
    sensitive.
    """
    return base_name(prod_path).casefold() == base_name(ptbl_path).casefold()


def check_matching_names(prod_path: str, ptbl_path: str) -> None:
    """Raise LoadError when the .prod and .ptbl names differ."""
    if not names_match(prod_path, ptbl_path):
        raise LoadError(
            f"File names do not match: {os.path.basename(prod_path)} and "
            f"{os.path.basename(ptbl_path)}. Both files must have the same name."
        )


def check_compatible(productions: list[Production], table: ParseTable) -> None:
    """Raise LoadError when the productions and parse table disagree.

    Checks that:
    - every production number in the table exists in the productions,
    - the production in a cell belongs to that row's non-terminal,
    - every non-terminal in the productions has a row in the table,
    - every right-hand side symbol is a non-terminal or a table terminal.
    """
    by_id = {p.id: p for p in productions}
    lhs = {p.non_terminal for p in productions}
    terminals = set(table.terminals)

    for nt in table.non_terminals:
        for t in table.terminals:
            number = table.get(nt, t)
            if number is None:
                continue
            if number not in by_id:
                raise LoadError(
                    f"Parse table cell [{nt}, {t}] uses production {number}, "
                    f"which is not in the productions file."
                )
            if by_id[number].non_terminal != nt:
                raise LoadError(
                    f"Parse table cell [{nt}, {t}] uses production {number} "
                    f"({by_id[number]}), which is not a production of {nt}."
                )

    missing_rows = [nt for nt in dict.fromkeys(p.non_terminal for p in productions)
                    if nt not in table.table]
    if missing_rows:
        raise LoadError(
            "Parse table has no row for non-terminal(s): " + ", ".join(missing_rows)
        )

    for p in productions:
        for symbol in p.rhs:
            if symbol == END_MARKER:
                raise LoadError(
                    f"Production {p.id} uses the end marker {END_MARKER} "
                    f"in its right-hand side."
                )
            if symbol not in lhs and symbol not in terminals:
                raise LoadError(
                    f"Production {p.id} ({p}) uses {symbol}, which is neither "
                    f"a non-terminal nor a terminal in the parse table."
                )


def check_pair(prod_path: str, productions: list[Production],
               ptbl_path: str, table: ParseTable) -> None:
    """Name check plus content check. Call this before enabling Parse."""
    check_matching_names(prod_path, ptbl_path)
    check_compatible(productions, table)
