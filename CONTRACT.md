# Panel Contract

All source files go in the same folder as `main_window.py`. No subfolders.

File name prefixes: `ui_` for user interface panels, `lex_` for lexical analysis logic and data.

Files marked **PLACEHOLDER** in their header are stubs. Replace each one with your own version and keep the file name, class name, and method below unchanged.

| Member | File | Class | Method called by MainWindow |
|---|---|---|---|
| B | `lex_scanner.py` | `Scanner` | `analyze(source_code)` returns a `LexResult` |
| B | `ui_token_panel.py` | `TokenPanel` | `show_tokens(tokens)` |
| C | `ui_console_panel.py` | `ConsolePanel` | `show_result(errors)` |
| D | `ui_variable_panel.py` | `VariablePanel` | `show_variables(variables)` |

## Rules

- GUI library: Tkinter (built into Python).
- Each panel extends `tk.LabelFrame` (or `tk.Frame`) and has the constructor `__init__(self, parent)`.
- Each `show_...` method replaces the old content. It does not append to it.
- `show_tokens` can receive an empty list. MainWindow sends one after each compile to clear old tokens.
- Data classes (Member B) are in `lex_data.py`: `Token`, `LexError`, `Variable`, `LexResult`.
  - MainWindow uses `token.type`, `token.line`, `result.tokens`, `result.errors`, `result.variables`.
  - Line numbers start at 1.
- Do not name any file `token.py`. It replaces Python's built-in `token` module and breaks the program.

## Run and Build

```
python main_window.py
```

Executable (requires `pip install pyinstaller`):

```
build.bat
```

Output: `dist\LexicalAnalyzer.exe`
