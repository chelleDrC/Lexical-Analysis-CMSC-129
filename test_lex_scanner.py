import unittest

from lex_data import LexError
from lex_scanner import Scanner
from ui_console_panel import ConsolePanel


class ScannerTests(unittest.TestCase):

    def setUp(self):
        self.scanner = Scanner()

    def test_official_iol_program(self):
        result = self.scanner.analyze(
            "IOL\n"
            "INT num IS 3\n"
            "STR message\n"
            "INTO num IS MULT num 2\n"
            "PRINT message\n"
            "LOI\n"
        )

        self.assertEqual(
            [token.type for token in result.tokens],
            [
                "IOL", "INT", "IDENT", "IS", "INT_LIT",
                "STR", "IDENT", "INTO", "IDENT", "IS",
                "MULT", "IDENT", "INT_LIT", "PRINT", "IDENT", "LOI",
            ],
        )
        self.assertEqual(result.errors, [])
        self.assertEqual(
            [(variable.name, variable.type) for variable in result.variables],
            [("num", "INT"), ("message", "STR")],
        )

    def test_keywords_are_case_sensitive(self):
        result = self.scanner.analyze("iol int x loi")

        self.assertEqual(
            [token.type for token in result.tokens],
            ["IDENT", "IDENT", "IDENT", "IDENT"],
        )
        self.assertEqual(result.errors, [])

    def test_invalid_lexemes_are_reported_with_line_numbers(self):
        result = self.scanner.analyze("IOL\nINT 2name\nPRINT @\nLOI")

        self.assertEqual(
            [(error.lexeme, error.line) for error in result.errors],
            [("2name", 2), ("@", 3)],
        )
        self.assertEqual(
            [(token.type, token.lexeme) for token in result.tokens],
            [
                ("IOL", "IOL"),
                ("INT", "INT"),
                ("ERR_LEX", "2name"),
                ("PRINT", "PRINT"),
                ("ERR_LEX", "@"),
                ("LOI", "LOI"),
            ],
        )

    def test_malformed_words_are_single_error_lexemes(self):
        result = self.scanner.analyze("IOL\nINT num$ IS 3#\nPRINT abc_def\nLOI")

        self.assertEqual(
            [(error.lexeme, error.line) for error in result.errors],
            [("num$", 2), ("3#", 2), ("abc_def", 3)],
        )
        self.assertEqual(
            [(token.type, token.lexeme) for token in result.tokens],
            [
                ("IOL", "IOL"),
                ("INT", "INT"),
                ("ERR_LEX", "num$"),
                ("IS", "IS"),
                ("ERR_LEX", "3#"),
                ("PRINT", "PRINT"),
                ("ERR_LEX", "abc_def"),
                ("LOI", "LOI"),
            ],
        )

    def test_blank_lines_preserve_source_line_numbers(self):
        result = self.scanner.analyze("IOL\n\nPRINT 1\nLOI")

        self.assertEqual(
            [(token.type, token.line) for token in result.tokens],
            [("IOL", 1), ("PRINT", 3), ("INT_LIT", 3), ("LOI", 4)],
        )

    def test_console_messages_are_built_from_errors(self):
        self.assertEqual(
            ConsolePanel.build_messages([]),
            ["Lexical analysis successful. No lexical errors found."],
        )

        messages = ConsolePanel.build_messages([LexError("bad$", 4), LexError("@", 5)])

        self.assertEqual(
            messages,
            [
                "Lexical analysis failed. Found 2 lexical error(s):",
                "ERR_LEX: unknown word 'bad$' at line 4",
                "ERR_LEX: unknown word '@' at line 5",
            ],
        )


if __name__ == "__main__":
    unittest.main()
