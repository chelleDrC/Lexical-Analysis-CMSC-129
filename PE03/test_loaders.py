"""Tests for Member 1: CsvReader, ProductionLoader, ParseTableLoader, checks.

Run with:  python -m unittest test_loaders -v
"""

import os
import shutil
import tempfile
import unittest

from csv_reader import CsvReader
from file_validation import (
    PROD_EXT, PTBL_EXT, LoadError, check_compatible, check_matching_names,
    check_pair, file_type, names_match, normalize_symbol,
)
from parse_data import Production
from parse_table_loader import ParseTableLoader
from production_loader import ProductionLoader

GOOD_PROD = (
    "1,E,T E'\n"
    "2,E',+ T E'\n"
    "3,E',e\n"
    "4,T,F T'\n"
    "5,T',* F T'\n"
    "6,T',e\n"
    "7,F,( E )\n"
    "8,F,id\n"
)

GOOD_PTBL = (
    ",id,+,*,(,),$\n"
    "E,1,,,1,,\n"
    "E',,2,,,3,3\n"
    "T,4,,,4,,\n"
    "T',,6,5,,6,6\n"
    "F,8,,,7,,\n"
)


class TempFiles(unittest.TestCase):
    """Gives each test its own folder and a helper to write files into it."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, name, text, encoding="utf-8"):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding=encoding, newline="") as f:
            f.write(text)
        return path

    def assertLoadError(self, func, *args, contains=""):
        with self.assertRaises(LoadError) as ctx:
            func(*args)
        if contains:
            self.assertIn(contains, str(ctx.exception))
        return str(ctx.exception)


class ProductionLoaderTests(TempFiles):

    def test_sample_file(self):
        prods = ProductionLoader.load(self.write("rules.prod", GOOD_PROD))
        self.assertEqual(len(prods), 8)
        self.assertEqual(prods[0], Production(1, "E", ["T", "E'"]))
        self.assertEqual(prods[6], Production(7, "F", ["(", "E", ")"]))
        self.assertEqual(prods[7], Production(8, "F", ["id"]))

    def test_empty_production_becomes_empty_list(self):
        prods = ProductionLoader.load(self.write("rules.prod", GOOD_PROD))
        self.assertEqual(prods[2].rhs, [])
        self.assertTrue(prods[2].is_empty)
        self.assertEqual(prods[2].rhs_text, "e")
        self.assertEqual(str(prods[2]), "E' > e")

    def test_extra_whitespace_in_rhs(self):
        prods = ProductionLoader.load(
            self.write("g.prod", "1, S ,  a   S\tb  \n2,S,e\n"))
        self.assertEqual(prods[0], Production(1, "S", ["a", "S", "b"]))

    def test_trailing_commas_and_blank_lines(self):
        prods = ProductionLoader.load(
            self.write("g.prod", "1,S,a S,,\n\n,,\n2,S,e,\n"))
        self.assertEqual([p.id for p in prods], [1, 2])

    def test_crlf_and_bom(self):
        text = "\ufeff" + GOOD_PROD.replace("\n", "\r\n")
        prods = ProductionLoader.load(self.write("rules.prod", text))
        self.assertEqual(prods[0].non_terminal, "E")
        self.assertEqual(len(prods), 8)

    def test_quoted_comma_terminal(self):
        prods = ProductionLoader.load(self.write("g.prod", '1,L,"id , L"\n2,L,id\n'))
        self.assertEqual(prods[0].rhs, ["id", ",", "L"])

    def test_curly_apostrophes_normalized(self):
        text = "1,E,T E\u2019\n2,E\u2019,+ T E'\n3,E\u2018,e\n"
        prods = ProductionLoader.load(self.write("g.prod", text))
        self.assertEqual(prods[0].rhs, ["T", "E'"])
        self.assertEqual(prods[1].non_terminal, "E'")
        self.assertEqual(prods[2].non_terminal, "E'")

    def test_curly_apostrophes_in_windows_encoding(self):
        text = "1,E,T E\u2019\n2,E\u2019,e\n"
        prods = ProductionLoader.load(self.write("g.prod", text, encoding="cp1252"))
        self.assertEqual(prods[1].non_terminal, "E'")

    def test_bad_extension(self):
        path = self.write("rules.txt", GOOD_PROD)
        self.assertLoadError(ProductionLoader.load, path, contains=".prod")

    def test_ptbl_given_to_production_loader(self):
        path = self.write("rules.ptbl", GOOD_PTBL)
        self.assertLoadError(ProductionLoader.load, path, contains="expected a .prod")

    def test_missing_file(self):
        path = os.path.join(self.dir, "nothing.prod")
        self.assertLoadError(ProductionLoader.load, path, contains="not found")

    def test_empty_file(self):
        self.assertLoadError(ProductionLoader.load, self.write("g.prod", ""),
                             contains="empty")
        self.assertLoadError(ProductionLoader.load, self.write("h.prod", "\n ,,\n"),
                             contains="empty")

    def test_missing_columns(self):
        msg = self.assertLoadError(ProductionLoader.load,
                                   self.write("g.prod", "1,S,a\n2,S\n"),
                                   contains="missing columns")
        self.assertIn("line 2", msg)

    def test_too_many_columns(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "1,S,a,b\n"),
                             contains="too many columns")

    def test_number_not_integer(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "one,S,a\n"),
                             contains="not a whole number")

    def test_number_zero(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "0,S,a\n"),
                             contains="1 or higher")

    def test_start_symbol(self):
        prods = ProductionLoader.load(self.write("g.prod", "2,A,a\n1,S,A b\n"))
        self.assertEqual(ProductionLoader.start_symbol(prods), "S")

    def test_no_production_1(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "2,S,a\n3,S,b\n"),
                             contains="no production 1")

    def test_duplicate_number(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "1,S,a\n1,S,b\n"),
                             contains="used twice")

    def test_empty_non_terminal(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "1, ,a\n"),
                             contains="non-terminal is empty")

    def test_non_terminal_with_space(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "1,S T,a\n"),
                             contains="one symbol")

    def test_empty_rhs(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "1,S,   \n"),
                             contains="production is empty")

    def test_e_mixed_with_symbols(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", "1,S,a e\n"),
                             contains="only symbol")

    def test_unclosed_quote(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", '1,S,"a\n2,S,b\n'),
                             contains="malformed CSV")

    def test_text_after_closing_quote(self):
        self.assertLoadError(ProductionLoader.load,
                             self.write("g.prod", '1,S,"a"b\n'),
                             contains="malformed CSV")

    def test_binary_file(self):
        path = os.path.join(self.dir, "g.prod")
        with open(path, "wb") as f:
            f.write(b"\x00\x01\x02\xff\xfe")
        self.assertLoadError(ProductionLoader.load, path, contains="not a text file")


class ParseTableLoaderTests(TempFiles):

    def test_sample_file(self):
        table = ParseTableLoader.load(self.write("rules.ptbl", GOOD_PTBL))
        self.assertEqual(table.terminals, ["id", "+", "*", "(", ")", "$"])
        self.assertEqual(table.non_terminals, ["E", "E'", "T", "T'", "F"])
        self.assertEqual(table.get("E", "id"), 1)
        self.assertEqual(table.get("E'", "$"), 3)
        self.assertEqual(table.get("T'", "*"), 5)
        self.assertEqual(table.get("F", "("), 7)

    def test_blank_cells_are_none(self):
        table = ParseTableLoader.load(self.write("rules.ptbl", GOOD_PTBL))
        self.assertIsNone(table.get("E", "+"))
        self.assertIsNone(table.get("F", "$"))
        self.assertEqual(table.cell_text("E", "+"), "")
        self.assertEqual(table.cell_text("E", "id"), "1")

    def test_unknown_lookups_are_none(self):
        table = ParseTableLoader.load(self.write("rules.ptbl", GOOD_PTBL))
        self.assertIsNone(table.get("X", "id"))
        self.assertIsNone(table.get("E", "x"))

    def test_top_left_cell_ignored(self):
        text = "NT" + GOOD_PTBL
        table = ParseTableLoader.load(self.write("rules.ptbl", text))
        self.assertEqual(table.terminals[0], "id")

    def test_extra_trailing_commas(self):
        text = ",id,$,,\nS,1,,,,\n"
        table = ParseTableLoader.load(self.write("g.ptbl", text))
        self.assertEqual(table.terminals, ["id", "$"])
        self.assertEqual(table.get("S", "id"), 1)

    def test_short_row_means_blank_cells(self):
        table = ParseTableLoader.load(self.write("g.ptbl", ",id,+,$\nS,1\n"))
        self.assertEqual(table.get("S", "id"), 1)
        self.assertIsNone(table.get("S", "$"))

    def test_spaces_in_cells(self):
        table = ParseTableLoader.load(self.write("g.ptbl", " , id , $ \n S , 1 ,  \n"))
        self.assertEqual(table.terminals, ["id", "$"])
        self.assertEqual(table.get("S", "id"), 1)

    def test_crlf_and_bom(self):
        text = "\ufeff" + GOOD_PTBL.replace("\n", "\r\n")
        table = ParseTableLoader.load(self.write("rules.ptbl", text))
        self.assertEqual(table.terminals[0], "id")
        self.assertEqual(table.non_terminals[0], "E")

    def test_curly_apostrophes_normalized(self):
        text = GOOD_PTBL.replace("E'", "E\u2019").replace("T'", "T\u2032")
        table = ParseTableLoader.load(self.write("rules.ptbl", text))
        self.assertEqual(table.non_terminals, ["E", "E'", "T", "T'", "F"])
        self.assertEqual(table.get("E'", "+"), 2)

    def test_bad_extension(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("rules.csv", GOOD_PTBL), contains=".ptbl")

    def test_prod_given_to_table_loader(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("rules.prod", GOOD_PROD),
                             contains="expected a .ptbl")

    def test_empty_file(self):
        self.assertLoadError(ParseTableLoader.load, self.write("g.ptbl", ""),
                             contains="empty")

    def test_header_only(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,$\n"),
                             contains="no non-terminal rows")

    def test_header_without_terminals(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", "S\nE,1\n"),
                             contains="missing columns")

    def test_header_gap(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,,$\nS,1,,\n"),
                             contains="column 3 has no terminal name")

    def test_duplicate_terminal(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,id,$\nS,1,,\n"),
                             contains="listed twice")

    def test_missing_end_marker(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,+\nS,1,\n"),
                             contains="end marker")

    def test_row_with_too_many_cells(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,$\nS,1,,2\n"),
                             contains="too many columns")

    def test_non_number_cell(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,$\nS,x,\n"),
                             contains="production number or blank")

    def test_zero_cell(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,$\nS,0,\n"),
                             contains="1 or higher")

    def test_empty_non_terminal(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,$\n,1,\n"),
                             contains="non-terminal is empty")

    def test_duplicate_row(self):
        self.assertLoadError(ParseTableLoader.load,
                             self.write("g.ptbl", ",id,$\nS,1,\nS,,2\n"),
                             contains="two rows")


class CsvReaderTests(TempFiles):

    def test_line_numbers_skip_blank_rows(self):
        rows = CsvReader.read_rows(self.write("a.prod", "1,S,a\n\n2,S,b\n"))
        self.assertEqual([line for line, _ in rows], [1, 3])

    def test_folder_is_rejected(self):
        self.assertRaises(LoadError, CsvReader.read_rows, self.dir)


class FileNameTests(unittest.TestCase):

    def test_file_type(self):
        self.assertEqual(file_type("C:/x/rules.prod"), PROD_EXT)
        self.assertEqual(file_type("C:/x/RULES.PTBL"), PTBL_EXT)
        self.assertRaises(LoadError, file_type, "C:/x/rules.txt")
        self.assertRaises(LoadError, file_type, "C:/x/rules")

    def test_matching_names(self):
        self.assertTrue(names_match("C:/a/rules.prod", "C:/b/rules.ptbl"))
        self.assertTrue(names_match("rules.prod", "Rules.ptbl"))
        check_matching_names("rules.prod", "rules.ptbl")

    def test_mismatched_names_rejected(self):
        self.assertFalse(names_match("a.prod", "b.ptbl"))
        with self.assertRaises(LoadError) as ctx:
            check_matching_names("C:/x/a.prod", "C:/x/b.ptbl")
        self.assertIn("a.prod", str(ctx.exception))
        self.assertIn("b.ptbl", str(ctx.exception))

    def test_name_with_dots(self):
        self.assertTrue(names_match("my.rules.prod", "my.rules.ptbl"))
        self.assertFalse(names_match("my.rules.prod", "my.ptbl"))

    def test_normalize_symbol(self):
        self.assertEqual(normalize_symbol(" E\u2019 "), "E'")
        self.assertEqual(normalize_symbol("T\u2018"), "T'")
        self.assertEqual(normalize_symbol("F`"), "F'")
        self.assertEqual(normalize_symbol("id"), "id")


class CompatibilityTests(TempFiles):

    def load_pair(self, prod_text=GOOD_PROD, ptbl_text=GOOD_PTBL):
        prod = self.write("rules.prod", prod_text)
        ptbl = self.write("rules.ptbl", ptbl_text)
        return prod, ProductionLoader.load(prod), ptbl, ParseTableLoader.load(ptbl)

    def test_sample_pair_is_compatible(self):
        check_pair(*self.load_pair())

    def test_sample_with_mixed_apostrophes_is_compatible(self):
        # The handout mixes E' and E’ between (and inside) the two files.
        prod = GOOD_PROD.replace("2,E',", "2,E\u2019,").replace("5,T',", "5,T\u2019,")
        ptbl = GOOD_PTBL.replace("E',", "E\u2019,")
        check_pair(*self.load_pair(prod, ptbl))

    def test_cell_with_unknown_production(self):
        _, prods, _, table = self.load_pair(ptbl_text=GOOD_PTBL.replace("F,8", "F,9"))
        self.assertLoadError(check_compatible, prods, table,
                             contains="not in the productions file")

    def test_cell_with_production_of_other_non_terminal(self):
        _, prods, _, table = self.load_pair(ptbl_text=GOOD_PTBL.replace("F,8", "F,1"))
        self.assertLoadError(check_compatible, prods, table,
                             contains="not a production of F")

    def test_missing_row(self):
        ptbl = GOOD_PTBL.replace("F,8,,,7,,\n", "")
        _, prods, _, table = self.load_pair(ptbl_text=ptbl)
        self.assertLoadError(check_compatible, prods, table, contains="no row")

    def test_rhs_symbol_not_in_table(self):
        prod = GOOD_PROD.replace("8,F,id", "8,F,num")
        _, prods, _, table = self.load_pair(prod_text=prod)
        self.assertLoadError(check_compatible, prods, table, contains="num")

    def test_paren_without_spaces(self):
        # The handout's 7,F,(E) is one symbol "(E)" unless spaces are added.
        prod = GOOD_PROD.replace("( E )", "(E)")
        _, prods, _, table = self.load_pair(prod_text=prod)
        self.assertLoadError(check_compatible, prods, table, contains="(E)")

    def test_mismatched_names_in_pair(self):
        prod = self.write("a.prod", GOOD_PROD)
        ptbl = self.write("b.ptbl", GOOD_PTBL)
        self.assertLoadError(
            check_pair, prod, ProductionLoader.load(prod),
            ptbl, ParseTableLoader.load(ptbl), contains="do not match")


class SampleFileTests(unittest.TestCase):
    """The rules.prod and rules.ptbl shipped next to the program."""

    def test_shipped_samples(self):
        here = os.path.dirname(os.path.abspath(__file__))
        prod = os.path.join(here, "rules.prod")
        ptbl = os.path.join(here, "rules.ptbl")
        check_pair(prod, ProductionLoader.load(prod), ptbl, ParseTableLoader.load(ptbl))


if __name__ == "__main__":
    unittest.main()
