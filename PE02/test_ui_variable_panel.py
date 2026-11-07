"""Unit tests for ui_variable_panel.py (Member D)."""

import unittest
import tkinter as tk

from lex_data import Variable
from ui_variable_panel import VariablePanel


class VariablePanelTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a hidden Tk root for widget instantiation
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.panel = VariablePanel(self.root)

    def tearDown(self):
        self.panel.destroy()

    def test_initial_state_is_empty(self):
        self.assertEqual(self.panel.count(), 0)
        self.assertEqual(self.panel.get_variables(), [])

    def test_show_variables_displays_entries(self):
        variables = [
            Variable("num", "INT"),
            Variable("result", "INT"),
            Variable("message", "STR"),
        ]
        self.panel.show_variables(variables)

        self.assertEqual(self.panel.count(), 3)
        self.assertEqual(
            self.panel.get_variables(),
            [("num", "INT"), ("result", "INT"), ("message", "STR")],
        )

    def test_show_variables_deduplicates_identifiers(self):
        """Ensures that duplicate variable names are not added to the table."""
        variables = [
            Variable("counter", "INT"),
            Variable("counter", "INT"),
            Variable("total", "INT"),
            Variable("counter", "STR"),  # Duplicate name with different or same type
        ]
        self.panel.show_variables(variables)

        # Only unique identifier names should be inserted
        self.assertEqual(self.panel.count(), 2)
        self.assertEqual(
            self.panel.get_variables(),
            [("counter", "INT"), ("total", "INT")],
        )

    def test_show_variables_replaces_old_content(self):
        """Ensures show_variables clears old content instead of appending."""
        self.panel.show_variables([Variable("old_var", "INT")])
        self.assertEqual(self.panel.get_variables(), [("old_var", "INT")])

        self.panel.show_variables([Variable("new_var", "STR")])
        self.assertEqual(self.panel.get_variables(), [("new_var", "STR")])

    def test_show_variables_with_empty_list_clears_table(self):
        self.panel.show_variables([Variable("temp", "INT")])
        self.assertEqual(self.panel.count(), 1)

        self.panel.show_variables([])
        self.assertEqual(self.panel.count(), 0)
        self.assertEqual(self.panel.get_variables(), [])

    def test_clear_method_removes_all_rows(self):
        self.panel.show_variables([Variable("a", "INT"), Variable("b", "STR")])
        self.assertEqual(self.panel.count(), 2)

        self.panel.clear()
        self.assertEqual(self.panel.count(), 0)


if __name__ == "__main__":
    unittest.main()
