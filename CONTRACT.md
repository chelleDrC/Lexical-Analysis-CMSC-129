# Panel Contract

All source files go in the same folder as `main_window.py`. No subfolders.

File name prefixes: `ui_` for user interface panels, `lex_` for lexical analysis logic and data.

| Member | Assigned Member | File | Class | Method called by MainWindow |
|---|---|---|---|---|
| A | Richelle De Arce | `main_window.py`, `ui_editor_panel.py` | `MainWindow`, `EditorPanel` | `main()`, `get_text()`, `set_text()` |
| B | Johnric Apolinario | `lex_scanner.py`, `ui_token_panel.py` | `Scanner`, `TokenPanel` | `analyze(source_code)` returns a `LexResult`, `show_tokens(tokens)` |
| C | John Andrei Manalo | `ui_console_panel.py` | `ConsolePanel` | `show_result(errors)` |
| D | Mark Jaily Pena | `ui_variable_panel.py` | `VariablePanel` | `show_variables(variables)` |

## Rules

- GUI library: Tkinter (built into Python standard library).
- Each panel extends `tk.LabelFrame` (or `tk.Frame`) and has the constructor `__init__(self, parent)`.
- Each `show_...` method replaces old content; it does not append to it.
- `show_tokens` can receive an empty list. MainWindow sends one after each compile to clear old tokens until requested.
- `show_variables` receives the list of variables and displays unique identifiers without duplicate rows.
- Data classes (Member B) are in `lex_data.py`: `Token`, `LexError`, `Variable`, `LexResult`.
  - MainWindow uses `token.type`, `token.line`, `result.tokens`, `result.errors`, `result.variables`.
  - Line numbers start at 1.
- Do not name any file `token.py`. It replaces Python's built-in `token` module and breaks the program.

## Run and Build

```bash
python main_window.py
```

Executable (requires `pip install pyinstaller`):

```cmd
build.bat
```

Submission Zip: `Apolinario_DeArce_Manalo_Pena_PE02.zip` containing `dist/LexicalAnalyzer.exe` (or `dist/LexicalAnalyzer`), source code files, and documentation.
