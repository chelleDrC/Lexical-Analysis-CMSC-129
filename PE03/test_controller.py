"""Tests for Member 4: Controller and PrsdWriter.

Run with:  python -m unittest test_controller -v

The view is replaced by a mock, and the file dialogs and message boxes are
patched, so these tests run without opening any windows.
"""

import csv
import os
import shutil
import tempfile
import unittest
from unittest import mock

import controller as controller_module
import prsd_writer as prsd_module
from controller import Controller
from parse_data import ParseResult, ParseStep
from prsd_writer import PrsdWriter

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PROD = os.path.join(HERE, "rules.prod")
SAMPLE_PTBL = os.path.join(HERE, "rules.ptbl")


def make_view(input_text=""):
    view = mock.MagicMock()
    view.root = None
    view.get_input_text.return_value = input_text
    return view


class ControllerTestBase(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.prod = os.path.join(self.folder, "rules.prod")
        self.ptbl = os.path.join(self.folder, "rules.ptbl")
        shutil.copy(SAMPLE_PROD, self.prod)
        shutil.copy(SAMPLE_PTBL, self.ptbl)

        self.messagebox = mock.patch.object(controller_module, "messagebox").start()
        self.addCleanup(mock.patch.stopall)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def load(self, ctrl, view, path):
        view.choose_file.return_value = path
        ctrl.on_load()


class TestLoading(ControllerTestBase):

    def test_cancel_keeps_loaded_file_and_does_not_clear(self):
        view = make_view()
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        view.reset_mock()

        view.choose_file.return_value = ""  # user pressed Cancel
        ctrl.on_load()

        self.assertIsNotNone(ctrl.productions)
        view.clear_solution_table.assert_not_called()
        view.set_productions.assert_not_called()

    def test_bad_file_after_good_load_keeps_old_file(self):
        view = make_view()
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        self.load(ctrl, view, self.ptbl)
        good_table = ctrl.table

        # Overwrite the same file with broken CSV: a quote that is never closed.
        with open(self.ptbl, "w", encoding="utf-8") as f:
            f.write('"id,+,$\nE,1,,\n')
        self.load(ctrl, view, self.ptbl)

        self.assertIs(ctrl.table, good_table)
        self.messagebox.showerror.assert_called_once()

    def test_every_load_attempt_clears_solution(self):
        view = make_view()
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        view.clear_solution_table.reset_mock()

        self.load(ctrl, view, self.prod)  # even a successful reload clears
        view.clear_solution_table.assert_called_once()

    def test_names_must_match(self):
        other = os.path.join(self.folder, "other.ptbl")
        shutil.copy(SAMPLE_PTBL, other)
        view = make_view()
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        self.load(ctrl, view, other)

        self.assertIn("do not match", ctrl.pair_problem)


class TestParseButton(ControllerTestBase):

    def test_parse_disabled_until_both_files_loaded(self):
        view = make_view("id")
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        view.set_parse_enabled.assert_called_with(False)

        self.load(ctrl, view, self.ptbl)
        view.set_parse_enabled.assert_called_with(True)

    def test_parse_disabled_for_empty_input(self):
        view = make_view("")
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        self.load(ctrl, view, self.ptbl)
        view.set_parse_enabled.assert_called_with(False)

        ctrl.on_input_change("   ")
        view.set_parse_enabled.assert_called_with(False)

        ctrl.on_input_change("id")
        view.set_parse_enabled.assert_called_with(True)

    def test_parse_disabled_when_names_do_not_match(self):
        other = os.path.join(self.folder, "other.ptbl")
        shutil.copy(SAMPLE_PTBL, other)
        view = make_view("id")
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        self.load(ctrl, view, other)

        view.set_parse_enabled.assert_called_with(False)


class TestParseAndSave(ControllerTestBase):

    def setUp(self):
        super().setUp()
        self.name_dialog = mock.patch.object(
            PrsdWriter, "ask_output_name", return_value="test"
        ).start()

    def loaded(self, input_text):
        view = make_view(input_text)
        ctrl = Controller(view)
        self.load(ctrl, view, self.prod)
        self.load(ctrl, view, self.ptbl)
        return view, ctrl

    def read_csv(self, path):
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.reader(f))

    def test_valid_input_writes_named_file_next_to_input(self):
        view, ctrl = self.loaded("id + id * id")
        ctrl.on_parse()

        expected = os.path.join(self.folder, "test_rules.prsd")
        self.assertTrue(os.path.exists(expected))
        self.assertEqual(
            view.set_parsing_message.call_args.args[0],
            "PARSING: Valid. Please see test_rules.prsd.",
        )
        rows = self.read_csv(expected)
        self.assertEqual(rows[0], ["E $", "id + id * id $", ""])
        self.assertEqual(rows[1], ["T E' $", "id + id * id $", "Output E > T E'"])
        self.assertEqual(rows[-1], ["", "", "Match $"])

    def test_invalid_input_ends_with_error_row(self):
        view, ctrl = self.loaded("id id")
        ctrl.on_parse()

        expected = os.path.join(self.folder, "test_rules.prsd")
        self.assertEqual(
            view.set_parsing_message.call_args.args[0],
            "PARSING: Invalid. Please see test_rules.prsd.",
        )
        rows = self.read_csv(expected)
        self.assertTrue(rows[-1][2].startswith("Error:"))

    def test_cancelled_output_name_saves_nothing(self):
        self.name_dialog.return_value = None
        view, ctrl = self.loaded("id")
        ctrl.on_parse()

        self.assertFalse(os.path.exists(os.path.join(self.folder, "test_rules.prsd")))
        self.assertEqual(
            view.set_parsing_message.call_args.args[0],
            "PARSING: Valid. Output was not saved.",
        )

    def test_solution_table_shows_steps(self):
        view, ctrl = self.loaded("id")
        ctrl.on_parse()
        steps = view.show_solution_rows.call_args.args[0]
        self.assertTrue(all(isinstance(s, ParseStep) for s in steps))


class TestPrsdWriter(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.prod = os.path.join(self.folder, "rules.prod")

    def test_output_path_format(self):
        path = PrsdWriter.output_path("test", self.prod)
        self.assertEqual(os.path.basename(path), "test_rules.prsd")
        self.assertEqual(os.path.dirname(path), self.folder)

    def test_commas_are_quoted(self):
        result = ParseResult(steps=[ParseStep("a, b", "$", "Match $")])
        path = PrsdWriter.write(result, "out", self.prod)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), '"a, b",$,Match $\n')


if __name__ == "__main__":
    unittest.main()
