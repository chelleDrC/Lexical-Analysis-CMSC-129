import unittest

from parse_data import ParseStep, ParseTable, Production
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
        self.assertEqual(result.steps[0].action, "")
        self.assertEqual(result.steps[1].action, "Output E > T E'")
        self.assertEqual(result.steps[-1], ParseStep("", "", "Match $"))

    def test_matches_handout_sample_output(self):
        # The sample solution from the handout for "id + id * id".
        expected = [
            ("E $", "id + id * id $", ""),
            ("T E' $", "id + id * id $", "Output E > T E'"),
            ("F T' E' $", "id + id * id $", "Output T > F T'"),
            ("id T' E' $", "id + id * id $", "Output F > id"),
            ("T' E' $", "+ id * id $", "Match id"),
            ("E' $", "+ id * id $", "Output T' > e"),
            ("+ T E' $", "+ id * id $", "Output E' > + T E'"),
            ("T E' $", "id * id $", "Match +"),
            ("F T' E' $", "id * id $", "Output T > F T'"),
            ("id T' E' $", "id * id $", "Output F > id"),
            ("T' E' $", "* id $", "Match id"),
            ("* F T' E' $", "* id $", "Output T' > * F T'"),
            ("F T' E' $", "id $", "Match *"),
            ("id T' E' $", "id $", "Output F > id"),
            ("T' E' $", "$", "Match id"),
            ("E' $", "$", "Output T' > e"),
            ("$", "$", "Output E' > e"),
            ("", "", "Match $"),
        ]
        result = PredictiveParser.parse(PRODUCTIONS, TABLE, "id + id * id")
        actual = [(s.stack, s.input, s.action) for s in result.steps]
        self.assertEqual(actual, expected)

    def test_invalid_input_ends_with_extra_error_row(self):
        result = self.assert_invalid_parse("id id")
        actual = [(s.stack, s.input, s.action) for s in result.steps]
        self.assertEqual(actual, [
            ("E $", "id id $", ""),
            ("T E' $", "id id $", "Output E > T E'"),
            ("F T' E' $", "id id $", "Output T > F T'"),
            ("id T' E' $", "id id $", "Output F > id"),
            ("T' E' $", "id $", "Match id"),
            ("", "", "Error: no production for T' with input id."),
        ])

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

    def test_rejects_input_after_end_marker(self):
        result = self.assert_invalid_parse("id $ id")
        self.assertIn("remains after the end marker", result.error_message)

    def test_stops_non_consuming_recursive_production(self):
        productions = [Production(1, "S", ["S"])]
        table = ParseTable(
            terminals=["$"],
            non_terminals=["S"],
            table={"S": {"$": 1}},
        )
        result = PredictiveParser.parse(productions, table, "")
        self.assertFalse(result.valid)
        self.assertIn("non-consuming recursive", result.error_message)


if __name__ == "__main__":
    unittest.main()