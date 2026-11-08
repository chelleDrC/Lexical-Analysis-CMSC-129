# Member 4: Program Flow, Output, and Packaging

## Module Description

`main.py` starts the program. `controller.py` connects the window (Member 3)
to the loaders (Member 1), the parser (Member 2), and the output writer. The
controller holds the currently loaded productions and parse table. A file is
stored only after it loads successfully, so a failed or cancelled load keeps
the previous file in use.

`prsd_writer.py` asks the user for the output name, builds the file name
`outname_prodname.prsd`, and writes the steps as CSV.

| File | Contents |
|---|---|
| `main.py` | Creates the `View` and the `Controller`, then starts the window. |
| `controller.py` | `Controller`: load handling, Parse enable rules, parse and save flow. |
| `prsd_writer.py` | `PrsdWriter`: output name prompt, file path, CSV writing. |
| `test_controller.py` | Tests for the controller and the writer (uses a mock view). |
| `build.bat` | Builds `dist\PredictiveParser.exe` with PyInstaller. |

## Control Flow

1. **Start:** `main.py` creates the view and the controller. Parse starts disabled.
2. **Load:** the user clicks Load and picks a file.
   - The solution table and PARSING message are cleared on every attempt.
   - Cancel: the loaded files stay as they were.
   - The file type is read from its extension (`.prod` or `.ptbl`).
   - The matching loader runs. On `LoadError` an error box is shown, the
     previous file stays loaded, and any file-mismatch message is shown again.
   - On success the file is stored and shown in its table, and the LOADED
     message is updated.
   - If both files are loaded, they are checked together (`check_pair`). A
     mismatch is shown in the PARSING message and Parse stays disabled.
3. **Enable Parse:** Parse is enabled only when both files are loaded and
   compatible and the input field is not empty. This is checked on every load
   and on every change to the input.
4. **Parse:** the input is parsed with `PredictiveParser.parse`. The steps are
   shown in the solution table.
5. **Save:** the user is asked for an output name.
   - Cancel: nothing is saved and the PARSING message says so.
   - Empty name, forbidden characters, or refusing to replace an existing
     file: the prompt is shown again.
   - Otherwise the file `outname_prodname.prsd` is written to the folder of
     the productions file, one row per step: stack, input buffer, action.
     The first row is the starting state with no action, and a valid run ends
     with `,,Match $`, as in the handout. Fields with commas are quoted
     automatically by the `csv` module.
6. **Result:** the PARSING message shows `Valid. Please see <file>.` or
   `Invalid. Please see <file>.`. For an invalid input, the file holds the
   steps up to where parsing stopped, then one extra row with empty Stack and
   Input and the `Error:` message in Action.

## Interface With Other Members

- Member 1: `ProductionLoader.load`, `ParseTableLoader.load`, `file_type`,
  `check_pair`, `base_name`, `LoadError`.
- Member 2: `PredictiveParser.parse(productions, table, text)` returns a
  `ParseResult`.
- Member 3: `View` methods and listeners (`set_on_load`, `choose_file`,
  `set_productions`, `set_parse_table`, `show_solution_rows`, and others).

## Testing

Run the tests from the `PE03` folder:

```
python -m unittest test_controller -v
```

| Area | Checked |
|---|---|
| Cancel after a good load | Old files stay loaded; solution table cleared. |
| Bad file after a good load | Old file stays loaded; error shown; mismatch message kept. |
| Load attempts | Solution table cleared on every real attempt. |
| Parse enable | Disabled until both files load; disabled for empty input; disabled for mismatched names. |
| Output name and location | `test_rules.prsd` in the productions file's folder. |
| Valid and invalid runs | Correct PARSING message; invalid file ends with an error row. |
| Cancelled name prompt | Nothing saved; message says the output was not saved. |
| CSV quoting | A field with a comma is quoted. |

End-to-end check: the built `PredictiveParser.exe` was copied with
`rules.prod` and `rules.ptbl` into an empty folder, started, and confirmed to
keep running. A scripted run with the real window loaded both files, parsed
`id + id * id`, and wrote `test_rules.prsd`.

## Building

Run `build.bat` (requires `pip install pyinstaller`). The result is
`dist\PredictiveParser.exe`. Only the Python standard library is used, so no
other dependency is needed.
