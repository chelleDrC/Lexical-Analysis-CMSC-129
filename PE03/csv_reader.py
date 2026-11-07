"""Reads a CSV file into rows of strings (Member 1)."""

import csv
import io
import os

from file_validation import LoadError

# utf-8-sig removes the byte order mark that Excel and Notepad may add.
# cp1252 is the Windows default, where curly quotes are single bytes.
_ENCODINGS = ("utf-8-sig", "cp1252")


class CsvReader:

    @staticmethod
    def read_text(path: str) -> str:
        """Return the file's text. Raises LoadError if it cannot be read."""
        name = os.path.basename(path)
        try:
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            raise LoadError(f"{name}: file not found.") from None
        except PermissionError:
            raise LoadError(f"{name}: permission denied.") from None
        except IsADirectoryError:
            raise LoadError(f"{name}: is a folder, not a file.") from None
        except OSError as e:
            raise LoadError(f"{name}: cannot be read ({e.strerror}).") from None

        for encoding in _ENCODINGS:
            try:
                return data.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise LoadError(f"{name}: not a text file.")

    @staticmethod
    def read_rows(path: str) -> list[tuple[int, list[str]]]:
        """Return ``(line_number, cells)`` for every non-blank row.

        Cells are kept as written (not stripped), so callers decide how to
        clean them. Rows that are empty or only commas and spaces are skipped.
        """
        name = os.path.basename(path)
        text = CsvReader.read_text(path)
        if "\x00" in text:
            raise LoadError(f"{name}: not a text file.")

        rows = []
        # strict=True reports quote mistakes, such as a quote that is never
        # closed, instead of silently joining the rest of the file into a cell.
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        try:
            for cells in reader:
                if any(cell.strip() for cell in cells):
                    rows.append((reader.line_num, cells))
        except csv.Error as e:
            raise LoadError(
                f"{name}, line {reader.line_num}: malformed CSV ({e})."
            ) from None

        if not rows:
            raise LoadError(f"{name}: file is empty.")
        return rows
