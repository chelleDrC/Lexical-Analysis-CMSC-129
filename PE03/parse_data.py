"""Shared data classes for PE03 (agreed on by all members).

Production and ParseTable are filled in by the loaders (Member 1).
ParseStep and ParseResult are filled in by the parser (Member 2).
"""

from dataclasses import dataclass, field

EMPTY_SYMBOL = "e"
END_MARKER = "$"


@dataclass
class Production:
    """One row of a .prod file, e.g. ``2,E',+ T E'``.

    ``rhs`` is the list of symbols on the right-hand side.
    The empty production ``e`` is stored as an empty list.
    """

    id: int
    non_terminal: str
    rhs: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.rhs

    @property
    def rhs_text(self) -> str:
        """Right-hand side as text, ``e`` for the empty production."""
        return " ".join(self.rhs) if self.rhs else EMPTY_SYMBOL

    def __str__(self) -> str:
        return f"{self.non_terminal} > {self.rhs_text}"


@dataclass
class ParseTable:
    """Contents of a .ptbl file.

    ``table[non_terminal][terminal]`` is a production number.
    Blank cells are not stored, so ``get`` returns ``None`` for them.
    """

    terminals: list[str] = field(default_factory=list)
    non_terminals: list[str] = field(default_factory=list)
    table: dict[str, dict[str, int]] = field(default_factory=dict)

    def get(self, non_terminal: str, terminal: str) -> int | None:
        return self.table.get(non_terminal, {}).get(terminal)

    def cell_text(self, non_terminal: str, terminal: str) -> str:
        """Cell as display text: the production number, or ``""`` if blank."""
        value = self.get(non_terminal, terminal)
        return "" if value is None else str(value)


@dataclass
class ParseStep:
    stack: str
    input: str
    action: str


@dataclass
class ParseResult:
    steps: list[ParseStep] = field(default_factory=list)
    valid: bool = False
    error_message: str = ""
