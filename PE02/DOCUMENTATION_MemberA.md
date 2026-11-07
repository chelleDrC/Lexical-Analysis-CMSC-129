# Member A: MainWindow and EditorPanel

## Description

`MainWindow` (`main_window.py`) is the compiler UI and the program entry point. It holds the toolbar, editor, and output panels. It reads and writes files, and it passes data between the editor, the Scanner, and the output panels.

`EditorPanel` (`ui_editor_panel.py`) is the editor area where source code is typed or loaded.

GUI library: Tkinter.

## Window Layout

| Area | Component |
|---|---|
| Top | Toolbar: Open File, New File, Compile Code, Show Tokenized Code |
| Left | `EditorPanel` |
| Right, top | `TokenPanel` (tokenized code) |
| Right, bottom | `VariablePanel` (table of variables) |
| Bottom | `ConsolePanel` and status bar |

Panes are resizable by dragging the borders. The program exits only when the user closes the window.

## MainWindow Attributes

| Attribute | Description |
|---|---|
| `root` | Tkinter main window |
| `editor_panel`, `token_panel`, `console_panel`, `variable_panel` | UI panels |
| `status_bar` | Label at the bottom of the window. Shows the last action, such as the path of the saved `.tkn` file. |
| `scanner` | Lexical analyzer (Member B) |
| `last_result` | Result of the last compile. `None` until Compile Code is clicked. Reset when a file is opened or a new file is created. |
| `current_file` | Path of the file loaded in the editor. `None` for a new file. Used to name the `.tkn` file. |

## MainWindow Functions

| Function | Description |
|---|---|
| `main()` | Starts the program and shows the window. |
| `__init__(root)` | Creates the panels, toolbar, status bar, and layout. |
| `create_toolbar()` | Builds the toolbar and links each button to its action. |
| `create_status_bar()` | Builds the status bar. |
| `create_main_area()` | Arranges the editor, output panels, and console using resizable panes. |
| `open_file()` | Shows a file dialog for `.iol` files, reads the selected file, and replaces the editor content. Shows an error if the file is not found or cannot be read. |
| `new_file()` | Asks to save the current code if the editor is not empty, then clears the editor. |
| `compile_code()` | Gets the current editor text, calls `scanner.analyze()`, saves the result in `last_result`, sends errors to `ConsolePanel` and variables to `VariablePanel`, clears `TokenPanel`, and writes the `.tkn` file. Shows a warning if the editor is empty. |
| `show_tokenized_code()` | Sends the tokens from `last_result` to `TokenPanel`. Shows "Compile the code first." if no compile has happened. |
| `read_file(path)` | Returns the full content of a text file. |
| `write_file(path, text)` | Writes text to a file, replacing its old content. |
| `save_file()` | Saves the editor content to an `.iol` file chosen by the user. Returns `True` if saved. |
| `write_token_file(tokens)` | Writes the token stream to `<filename>.tkn` in the same folder as the opened file, or `untitled.tkn` in the program folder for a new file. |
| `build_token_stream(tokens)` | Replaces each lexeme with its token name. Tokens stay on their original line numbers, and blank lines are kept. |
| `show_error(message)` | Shows an error dialog. |
| `set_status(message)` | Updates the status bar. |

## EditorPanel Functions

| Function | Description |
|---|---|
| `__init__(parent)` | Creates a monospaced text box with a vertical scrollbar. |
| `get_text()` | Returns the current editor text. |
| `set_text(content)` | Replaces the editor text and moves the cursor to the top. |
| `clear()` | Removes all text. |

## Control Flow

```
Program start
  -> main() creates MainWindow and shows it
  -> Wait for user action

Open File
  -> Choose .iol file -> read file -> replace editor text
  -> current_file = selected file, last_result = None

New File
  -> Editor not empty? Ask to save (Yes: save, No: discard, Cancel: stop)
  -> Clear editor, current_file = None, last_result = None

Compile Code
  -> Get editor text
  -> Empty? Show warning and stop
  -> last_result = scanner.analyze(text)
  -> console_panel.show_result(errors)
  -> variable_panel.show_variables(variables)
  -> Write token stream to .tkn file

Show Tokenized Code
  -> last_result is None? Show "Compile the code first." and stop
  -> token_panel.show_tokens(tokens)

Close window
  -> Program exits
```

Compile Code always reads the editor text when the button is clicked, so edits made after opening a file are included.

## Token File Format

Each lexeme is replaced by its token name. Line structure follows the source code.

```
Source (.iol)            Tokens (.tkn)
DEFINE x INTO            DEFINE IDENT INTO
x IS 5                   IDENT IS INT_LIT
```

## Test Cases

| Case | Expected result |
|---|---|
| Open a file, then compile | File loads into the editor. Console, variable table, and `.tkn` file are updated. |
| New file, type code, then compile | Same as above. `untitled.tkn` is written. |
| Compile an empty editor | Warning dialog. No crash. |
| Open a second file | Second file replaces the first in the editor. |
| Show Tokenized Code before compiling | "Compile the code first." dialog. |
| Show Tokenized Code after compiling | Tokens are shown in the Tokenized Code panel. |
| Code with errors | Console lists each unknown word and its line number. |
| Code without errors | Console shows the success message. |
