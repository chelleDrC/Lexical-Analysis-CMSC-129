"""
lex_scanner.py (Member B)

PLACEHOLDER - replace this file with Member B's version.
main_window.py uses: Scanner().analyze(source_code) -> LexResult

Dummy version: splits each line by whitespace, marks every word as IDENT,
and every word containing "?" as ERR_LEX. Used only to test the UI flow.
"""

from lex_data import Token, LexError, Variable, LexResult


class Scanner:

    def analyze(self, source_code):
        tokens = []
        errors = []
        variables = []

        lines = source_code.split("\n")
        for index in range(len(lines)):
            line_number = index + 1

            for word in lines[index].split():
                if "?" in word:
                    tokens.append(Token("ERR_LEX", word, line_number))
                    errors.append(LexError(word, line_number))
                else:
                    tokens.append(Token("IDENT", word, line_number))

        variables.append(Variable("dummyVar", "INT"))
        return LexResult(tokens, errors, variables)
