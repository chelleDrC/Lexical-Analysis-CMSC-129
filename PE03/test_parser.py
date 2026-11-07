import unittest

from parse_data import ParseTable, Production
from parser import PredictiveParser, Tokenizer


PRODUCTIONS = [
    Production(1, "E", ["T", "E'"]),
    Production(2, "E'", ["+", "T", "E'"]),
    Production(3, "E'", []),
    Production(4, "T", ["F", "T'"]),
    Production(5, "T'", ["*", "F", "T'"]),
    Production(6, "T'", []),
    Production(7, "F", ["(", "E", ")"]),
    Production(8, "F", ["id"]),
]
TABLE = ParseTable(
    terminals=["id", "+", "*", "(", ")", "$"],
    non_terminals=["E", "E'", "T", "T'", "F"],
    table={
        "E": {"id": 1, "(": 1},
        "E'": {"+": 2, ")": 3, "$": 3},
        "T": {"id": 4, "(": 4},
        "T'": {"+": 6, "*": 5, ")": 6, "$": 6},
        "F": {"id": 8, "(": 7},
    },
)


class TokenizerTests(unittest.TestCase):
    def test_splits_whitespace_and_appends_end_marker(self):
        self.assertEqual(Tokenizer.tokenize("  id\t+\n id  "), ["id", "+", "id", "$"])

    def test_normalizes_apostrophes(self):
        self.assertEqual(Tokenizer.tokenize("E\u2019"), ["E'", "$"])


class PredictiveParserTests(unittest.TestCase):
    def assert_invalid_parse(self, source):
        result = PredictiveParser.parse(PRODUCTIONS, TABLE, source)
        self.assertFalse(result.valid)
        return result

    def test_valid_expression(self):
        result = PredictiveParser.parse(PRODUCTIONS, TABLE, Tokenizer.tokenize("id + id * id"))
        self.assertTrue(result.valid)
        self.assertEqual(result.steps[0].action, "Output E > T E'")
        self.assertEqual(result.steps[-1].action, "Match $")

    def test_empty_input_is_invalid(self):
        result = self.assert_invalid_parse("")
        self.assertIn("no production", result.error_message)
        self.assertTrue(result.steps[-1].action.startswith("Error:"))

    def test_terminal_mismatch_is_invalid(self):
        result = self.assert_invalid_parse("id +")
        self.assertIn("no production", result.error_message)

    def test_parentheses(self):
        result = PredictiveParser.parse(PRODUCTIONS, TABLE, "( id )")
        self.assertTrue(result.valid)


if __name__ == "__main__":
    unittest.main()