# Member 3: GUI (View)

## Module Description

`view.py` contains the Tkinter `View` class for the predictive parser. It owns
the application window and widgets, and exposes display methods and event
listeners for a controller. It does not load files, validate grammar data, run
the parser, or save parse results.

The controller can attach its handlers with `set_on_load`, `set_on_parse`, and
`set_on_input_change`. The Load handler can call `choose_file()` to display the
single file chooser, which accepts `.prod` and `.ptbl` files. It can then call
`set_productions`, `set_parse_table`, and `set_loaded_message` with data
provided by the loader and validation modules. The parse handler can read the
input with `get_input_text()`, then update the status and solution table using
`set_parsing_message`, `show_solution_rows`, and `clear_solution_table`.

## Screen Layout

- The top section places the Productions table and Parse Table side by side.
- The Productions table has ID, NT, and P columns.
- The Parse Table uses the model's terminal order for columns and its
  non-terminal order for rows. Its non-terminal heading is intentionally
  blank to match the empty top-left cell in the `.ptbl` format. Blank cells
  are rendered as empty strings.
- The LOADED message and one Load button appear below the two tables.
- The INPUT field and Parse button occupy the next row. Parse starts disabled;
  the controller enables it after the files pass its loading and compatibility
  checks.
- The PARSING message appears above the solution table, which contains Stack,
  Input Buffer, and Action columns. Stack values and their heading are
  right-aligned.
- Tables have vertical and horizontal scrollbars. Grid weights let the tables
  grow with the window, and the input field expands horizontally when resized.

## View Methods

| Method | Purpose |
|---|---|
| `set_productions(productions, filename=None)` | Replace the productions display. |
| `set_parse_table(table, filename=None)` | Replace the parse table display, including blank cells. |
| `set_loaded_message(message)` | Set the LOADED text. |
| `set_parsing_message(message)` | Set the PARSING text. |
| `show_solution_rows(rows)` | Display `ParseStep` objects or three-value rows. |
| `clear_solution_table()` | Clear previous solution rows. |
| `set_parse_enabled(enabled)` | Enable or disable Parse. |
| `set_on_load(listener)` | Attach the Load button handler. |
| `set_on_parse(listener)` | Attach the Parse button handler. |
| `set_on_input_change(listener)` | Attach a handler receiving current input text. |
| `get_input_text()` | Read the current input field value. |
| `choose_file()` | Show the `.prod`/`.ptbl` file chooser. |
