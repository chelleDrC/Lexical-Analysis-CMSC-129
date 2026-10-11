import unittest

from lex_scanner import Scanner


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

    def test_blank_lines_preserve_source_line_numbers(self):
        result = self.scanner.analyze("IOL\n\nPRINT 1\nLOI")

        self.assertEqual(
            [(token.type, token.line) for token in result.tokens],
            [("IOL", 1), ("PRINT", 3), ("INT_LIT", 3), ("LOI", 4)],
        )


if __name__ == "__main__":
    unittest.main()
