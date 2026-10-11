"""Lexical analyzer for the official IOL language specification.

IOL (Integer-Oriented Language) is case-sensitive. Whitespace separates
lexemes, and the scanner returns one of the following token categories:

* the keyword itself, for reserved words such as ``INT`` and ``PRINT``
* ``IDENT`` for variable names
* ``INT_LIT`` for integer literals
* ``ERR_LEX`` for invalid lexemes

The scanner also collects variable declarations for the variables panel.
Syntax and semantic checks such as whether a variable was declared before
use belong to later compiler phases.
"""

from lex_data import LexError, LexResult, Token, Variable


KEYWORDS = {
    "IOL",
    "LOI",
    "INT",
    "STR",
    "INTO",
    "IS",
    "BEG",
    "PRINT",
    "NEWLN",
    "ADD",
    "SUB",
    "MULT",
    "DIV",
    "MOD",
}


class Scanner:
    """Scans IOL source code into tokens, errors, and variable declarations."""

    def analyze(self, source_code):
        tokens = []
        errors = []
        variables = []

        lines = source_code.splitlines()
        for line_number, line in enumerate(lines, start=1):
            position = 0

            while position < len(line):
                character = line[position]

                if character.isspace():
                    position += 1
                    continue

                if character.isalpha():
                    start = position
                    position += 1
                    while position < len(line) and (
                        line[position].isalpha() or line[position].isdigit()
                    ):
                        position += 1

                    lexeme = line[start:position]
                    token_type = lexeme if lexeme in KEYWORDS else "IDENT"
                    tokens.append(Token(token_type, lexeme, line_number))
                    continue

                if character.isdigit():
                    start = position
                    position += 1
                    while position < len(line) and line[position].isdigit():
                        position += 1

                    # An identifier must begin with a letter. A digit
                    # immediately followed by letters is one invalid lexeme,
                    # not a valid integer followed by an identifier.
                    if position < len(line) and line[position].isalpha():
                        while position < len(line) and (
                            line[position].isalpha() or line[position].isdigit()
                        ):
                            position += 1
                        lexeme = line[start:position]
                        tokens.append(Token("ERR_LEX", lexeme, line_number))
                        errors.append(LexError(lexeme, line_number))
                        continue

                    lexeme = line[start:position]
                    tokens.append(Token("INT_LIT", lexeme, line_number))
                    continue

                # IOL has word-based operations. Symbols such as +, =, and
                # quotation marks are not valid IOL lexemes.
                start = position
                position += 1
                while position < len(line) and not line[position].isspace():
                    position += 1

                lexeme = line[start:position]
                tokens.append(Token("ERR_LEX", lexeme, line_number))
                errors.append(LexError(lexeme, line_number))

        variables = self._collect_variables(tokens)
        return LexResult(tokens, errors, variables)

    def _collect_variables(self, tokens):
        """Collect declarations of the form ``INT name`` or ``STR name``."""
        variables = []
        declared_names = set()

        for index, token in enumerate(tokens):
            if token.type not in ("INT", "STR"):
                continue

            if index + 1 >= len(tokens):
                continue

            name_token = tokens[index + 1]
            if name_token.type != "IDENT" or name_token.lexeme in declared_names:
                continue

            variables.append(Variable(name_token.lexeme, token.type))
            declared_names.add(name_token.lexeme)

        return variables
