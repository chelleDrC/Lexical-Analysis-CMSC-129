"""Data classes shared by the IOL scanner and compiler UI panels."""


class Token:
    """One lexeme found in the source code and its token name."""

    def __init__(self, type, lexeme, line):
        self.type = type        # token name, e.g. IDENT, INT_LIT, DEFINE, ERR_LEX
        self.lexeme = lexeme    # actual text from the source code
        self.line = line        # line number where the lexeme was found (starts at 1)


class LexError:
    """An unknown word found in the source code and its line number."""

    def __init__(self, lexeme, line):
        self.lexeme = lexeme
        self.line = line


class Variable:
    """A declared variable: its name and data type."""

    def __init__(self, name, type):
        self.name = name
        self.type = type


class LexResult:
    """Everything produced by one run of the Scanner."""

    def __init__(self, tokens, errors, variables):
        self.tokens = tokens        # list of Token
        self.errors = errors        # list of LexError
        self.variables = variables  # list of Variable
